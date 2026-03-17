import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, TextIO


class LogFormatter(logging.Formatter):
    """Log formatter that adds colors based on log levels."""

    cyan, blue, gray, yellow, red, bold_red = (
        "\x1b[36m",
        "\x1b[34m",
        "\x1b[37m",
        "\x1b[33m",
        "\x1b[31m",
        "\x1b[31;1m",
    )

    reset = "\x1b[0m"

    bold = "\033[1m"
    reset_bold = "\033[0m"

    def __init__(self, class_length: int) -> None:
        """Initialize the LogFormatter with a specified class name length for formatting.

        Args:
            class_length (int): The maximum length of the logger name to display in the log output. If the logger name exceeds this length, it will be truncated from the left.

        Notes:
            - The formatter will apply different colors to the log output based on the log level (e.g., TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL).
            - The log format includes the timestamp, log level, logger name (formatted with bold), and the log message.

        """
        super().__init__()
        self.class_length: int = class_length

        self._fmt_str = f"%(asctime)s - [%(levelname)8s] - {self.bold}%(name){self.class_length}s{self.reset_bold} - %(message)s"

    def format(self, record: logging.LogRecord) -> str:
        """Override the format method to apply color formatting based on log levels and truncate logger names if they exceed the specified class length."""
        if len(record.name) > self.class_length:
            record.name = record.name[-self.class_length :]

        original_msg = record.getMessage()
        if "[" in original_msg and "]" in original_msg:
            colored_brackets = re.sub(
                r"\[(.*?)\]",
                f"[{self.cyan}\\1{self.reset}]",
                original_msg,
            )
            # Temporarily overwrite message for the formatter
            record.msg = colored_brackets
            record.args = ()  # Clear args since getMessage() already evaluated them
        formats = {
            5: f"{self.cyan}{self._fmt_str}{self.reset}",
            logging.DEBUG: f"{self.blue}{self._fmt_str}{self.reset}",
            logging.INFO: f"{self.gray}{self._fmt_str}{self.reset}",
            logging.WARNING: f"{self.yellow}{self._fmt_str}{self.reset}",
            logging.ERROR: f"{self.red}{self._fmt_str}{self.reset}",
            logging.CRITICAL: f"{self.bold_red}{self._fmt_str}{self.reset}",
        }
        log_fmt = formats.get(record.levelno, self._fmt_str)

        return logging.Formatter(log_fmt).format(record)

    @property
    def fmt_str(self) -> str:
        """Return the base log format string without color codes, which includes the timestamp, log level, logger name (formatted with bold), and the log message."""
        return self._fmt_str


class JsonFormatter(logging.Formatter):
    """Log formatter that outputs logs in JSON format, including timestamp, level, name, message, and any extra data."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON string, including timestamp, level, name, message, and any extra data if provided."""
        log_record: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=datetime.now().astimezone().tzinfo).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        # If the user passed extra={} data, include it
        if hasattr(record, "extra_data"):
            log_record["extra"] = getattr(record, "extra_data", None)

        return json.dumps(log_record)


class CustomLogger(logging.Logger):
    """Custom logger that supports a TRACE level and sets up logging with both console and file handlers."""

    TRACE: ClassVar[int] = 5
    logging.addLevelName(TRACE, "TRACE")

    def trace(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Log a message with severity 'TRACE'."""
        if self.isEnabledFor(self.TRACE):
            self._log(self.TRACE, msg, args, **kwargs)

    @staticmethod
    def setup_logging(folder: str, filename: str, level: str, class_length: int) -> None:
        """Set up logging with a handler that uses the custom LogFormatter and a file handler that writes logs in JSON format using the JsonFormatter.

        Args:
            folder (str): The directory where log files will be stored. If the directory does not exist, it will be created.
            filename (str): The base name for the log files. The actual log file will include a timestamp to ensure uniqueness.
            level (str): The logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL") that determines the minimum severity of messages to be logged.
            class_length (int): The maximum length of the logger name to display in the log output. If the logger name exceeds this length, it will be truncated from the left.

        Description:
            - This method configures the logging system to use a custom logger class (CustomLogger) and sets up two handlers: a console handler that formats logs with colors based
            on log levels, and

        """
        logging.setLoggerClass(CustomLogger)
        log_formatter = LogFormatter(class_length)

        root: logging.Logger = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)

        log_dir = Path(folder)
        log_dir.mkdir(parents=True, exist_ok=True)
        date_time: str = datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y%m%d-%H%M%S")
        file_handler = logging.FileHandler(log_dir / f"{filename}-{date_time}.log", mode="w")
        file_handler.setFormatter(logging.Formatter(log_formatter.fmt_str))

        console_handler: logging.StreamHandler[TextIO] = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)

        log_path: Path = Path(folder) / f"{filename}.jsonl"
        file_h = logging.FileHandler(log_path, mode="a")
        file_h.setFormatter(JsonFormatter())

        logging.basicConfig(level=level, handlers=[console_handler, file_handler, file_h])
