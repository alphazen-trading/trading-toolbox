from typing import Any
from loguru import logger as _logger
import traceback
import os
import orjson
import rich.logging
import rich.traceback
from rich import print as rprint
from rich.traceback import Traceback
from rich.console import Console
from rich.logging import RichHandler
from rich.pretty import pretty_repr

console = Console()


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


# List of modules to suppress in Rich traceback for cleaner output
SUPPRESSED_MODULES = [
    # "fire",
    # "monai.bundle",
    # "lighter.utils.cli",
    # "lighter.utils.runner",
    # "pytorch_lightning.trainer",
    # "lightning_utilities",
]


class Logger:
    """
    Custom Logger class utilizing Rich and Loguru for advanced logging.

    This class sets up a logging system that uses both the `Rich` library
    for enhanced output formatting in the console and `Loguru` for handling
    log files and more sophisticated logging features. The logger is configured
    to display colored and detailed logs in the terminal, while also saving
    structured logs to a file for debugging purposes.

    Key Features:

    - **Rich Tracebacks**: Automatically installs Rich traceback for more readable
      error messages in the console, highlighting key information such as line numbers
      and functions.
    - **Log File Handling**: Logs are saved in a specified directory with detailed
      information in JSON-like format, serialized for easier parsing.
    - **Log Levels**: Configured to handle different log levels, focusing on `INFO`
      messages for the console and `DEBUG` level messages for log files.



    **Usage Example**
    ```python
    from tradingtoolbox.utils.logger import logger, Logger

    # [Optional] Create a custom logger
    custom_logger = Logger(supressed_modules=["talib"], log_dir="./my_logs")

    try:
        # Code that might fail
        print(a)
    except Exception as e:
        logger.error()

    logger.warning("This is a warning message")
    logger.info({"key": "value"})
    logger.print("This replaces the standard print")
    ```

    **Notes:**

    - The logger's console output is colorized using `Rich`, and it includes rich tracebacks
      for easier debugging.
    - Log files are stored in the `log_dir` directory, defaulting to `./logs`.
    """

    def __init__(
        self,
        suppressed_modules: list[str] = SUPPRESSED_MODULES,
        log_dir: str = "./logs",
    ):
        """
        Initializes the custom logger instance.

        Parameters:
            suppressed_modules:
                A list of modules to suppress from rich traceback (default is SUPPRESSED_MODULES).
            log_dir:
                The directory where log files will be saved (default is "./logs").
        """

        self._create_logs_dir(log_dir)

        # This will install rich to traceback, which is quite handy
        rich.traceback.install(
            show_locals=False,
            suppress=[__import__(name) for name in suppressed_modules],
        )

        config = {
            "handlers": [
                {
                    "sink": RichHandler(
                        show_level=False,
                        show_time=True,
                        rich_tracebacks=True,
                        markup=True,
                        omit_repeated_times=False,
                    ),
                    # "sink": sys.stdout,
                    # This will force us to only use the rich handler on normal levels
                    "filter": lambda record: record["level"].name == "INFO",
                    "format": "{message}",
                },
                # {
                #     "sink": sys.stdout,
                #     "colorize": True,
                #     "backtrace": True,
                #     "diagnose": True,
                #     "enqueue": False,
                #     "format": "<cyan>❯ {module}:{function} ({line})</cyan> | <green>{time:YYYY-MM-DD at HH:mm:ss.sss}</green>",
                #     "filter": lambda record: record["level"].name == "INFO",
                # },
                {
                    "sink": "./logs/logs.log",
                    "level": "DEBUG",
                    "serialize": True,
                    "enqueue": True,
                    "colorize": True,
                    "format": "<light-cyan>❯ {module}:{function} ({line})</light-cyan> | <light-black>{time:YYYY-MM-DD at HH:mm:ss.sss}</light-black>\n{message}",
                },
            ],
        }

        _logger.configure(**config)  # type: ignore
        self.logger = _logger.patch(patching)

    def _create_logs_dir(self, directory="./logs"):
        os.makedirs(directory, exist_ok=True)

    def error(self):
        """
        Logs the most recent traceback error in a readable format, useful for. Uses the ERROR level
        """
        console.print(Traceback())
        recent_traceback = traceback.format_exc(limit=10)
        self.logger.error(recent_traceback)

    def warning(self, obj):
        """
        Logs a warning message with the option to pretty-print an object. Uses the WARNING level
        """
        self.logger.opt(depth=2).warning(pretty_repr(obj))

    def info(self, *obj):
        """
        Logs an informational message, replacing the standard print function. Uses the INFO level
        """
        for item in obj:
            self.logger.opt(depth=2).info(pretty_repr(item))
        # rprint(obj)


pprint = print

logger = Logger()
"""
An instantiated logger that you can use directly
"""


def print(*msg: Any) -> None:
    """
    Logs the provided object using an advanced logging mechanism.

    This method overrides the default `print` function to utilize a
    logger for output. It ensures that all output is captured
    through the logging system rather than standard output.

    Parameters:
        msg: The object to be logged. It can be of any type that the
            logger can handle, including strings, numbers, or custom objects.


    **Usage Example**
    ```python
    from tradingtoolbox.utils.logger import print

    print("Hello world")
    ```
    """
    logger.info(*msg)
