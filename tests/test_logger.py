import pytest
from tradingtoolbox.utils.logger import Logger
import sys
from io import StringIO
import traceback


@pytest.fixture
def logger():
    """Create a logger instance for testing"""
    return Logger(log_dir="./tests/logs")


@pytest.fixture
def capture_output():
    """Capture stdout for testing print output"""
    stdout = StringIO()
    old_stdout = sys.stdout
    sys.stdout = stdout
    yield stdout
    sys.stdout = old_stdout


def test_info_single_argument(logger, capture_output):
    """Test info logging with a single argument"""
    test_msg = "test message"
    logger.info(test_msg)
    assert "test message" in capture_output.getvalue()


def test_info_multiple_arguments(logger, capture_output):
    """Test info logging with multiple arguments"""
    logger.info(42, "hello", ["list", "items"])
    output = capture_output.getvalue()
    assert "42" in output
    assert "hello" in output
    assert "list" in output


def test_info_tuple(logger, capture_output):
    """Test info logging with tuple input"""
    test_tuple = (1, "two", 3.0)
    logger.info(test_tuple)
    output = capture_output.getvalue()
    assert "1" in output
    assert "two" in output
    assert "3.0" in output


def test_warning_messages(logger, capture_output):
    """Test warning logging with different types"""
    test_data = [
        123,
        "warning message",
        {"key": "value"},
        (1, 2, 3)
    ]
    for data in test_data:
        logger.warning(data)
    output = capture_output.getvalue()
    assert "123" in output
    assert "warning message" in output
    assert "key" in output
    assert "value" in output
    assert "(1, 2, 3)" in output


def test_error_with_exception(logger, capture_output):
    """Test error logging with an actual exception"""
    try:
        # Cause a deliberate exception
        1/0
    except Exception:
        logger.error("Custom error message")
        output = capture_output.getvalue()
        assert "ZeroDivisionError" in output
        assert "Custom error message" in output


def test_error_multiple_arguments(logger, capture_output):
    """Test error logging with multiple arguments"""
    try:
        # Cause a deliberate exception
        1/0
    except Exception:
        logger.error("Error occurred", {"details": "division by zero"}, 42)
        output = capture_output.getvalue()
        assert "ZeroDivisionError" in output
        assert "Error occurred" in output
        assert "division by zero" in output
        assert "42" in output


def test_mixed_type_logging(logger, capture_output):
    """Test logging with mixed types in a single call"""
    test_data = [
        42,
        "string",
        {"dict": "value"},
        (1, 2, 3),
        [4, 5, 6]
    ]
    logger.info(*test_data)
    output = capture_output.getvalue()
    
    for item in test_data:
        assert str(item) in output.replace("'", '"') 