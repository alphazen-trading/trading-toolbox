# type: ignore
from loguru import logger as _logger
import orjson
import sys


def patching(record):
    msg = record.get("message")

    # Convert single quotes to double quotes for JSON compatibility
    msg = msg.replace("'", '"')

    try:
        # Attempt to parse the message as JSON
        json_res = orjson.loads(msg)
    except ValueError:
        # If parsing fails, return without modifying the record further
        json_res = {}

    # Ensure the 'extra' field is initialized
    if "extra" not in record:
        record["extra"] = {}

    # If the message was successfully parsed as JSON, add its contents to the 'extra' field

    if isinstance(json_res, dict):
        for key, value in json_res.items():
            record["extra"][key] = value

    # Add the log level to the 'extra' field
    record["extra"]["_level"] = record["level"].name


def create_logger():
    config = {
        "handlers": [
            {
                "sink": sys.stdout,
                "colorize": True,
                "backtrace": True,
                "diagnose": True,
                "enqueue": False,
                "format": "<cyan>❯ {module}:{function} ({line})</cyan> | <green>{time:YYYY-MM-DD at HH:mm:ss.sss}</green>\n{message}\n",
            },
            {
                "sink": "/opt/logs/logs.log",
                "serialize": True,
                "enqueue": True,
                "colorize": True,
                "format": "<light-cyan>❯ {module}:{function} ({line})</light-cyan> | <light-black>{time:YYYY-MM-DD at HH:mm:ss.sss}</light-black>\n{message}",
            },
        ],
    }
    _logger.configure(**config)
    logger = _logger.patch(patching)
    return logger


pprint = print


def print(obj):
    logger.opt(depth=1).info(obj)


logger = create_logger()
