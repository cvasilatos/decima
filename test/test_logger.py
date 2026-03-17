"""Tests for decima logger module."""

import json
import logging
import tempfile
from pathlib import Path
from typing import cast

from decima import CustomLogger, JsonFormatter, LogFormatter
from decima.logger import blue, bold_red, cyan, gray, red, reset, yellow


class TestLogFormatter:
    """Tests for LogFormatter."""

    def test_format_debug_contains_blue(self) -> None:
        """DEBUG level records use blue color code."""
        formatter = LogFormatter(class_length=15)
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="debug msg",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert blue in result
        assert "debug msg" in result

    def test_format_info_contains_gray(self) -> None:
        """INFO level records use gray color code."""
        formatter = LogFormatter(class_length=15)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="info msg",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert gray in result
        assert "info msg" in result

    def test_format_warning_contains_yellow(self) -> None:
        """WARNING level records use yellow color code."""
        formatter = LogFormatter(class_length=15)
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="warn msg",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert yellow in result

    def test_format_error_contains_red(self) -> None:
        """ERROR level records use red color code."""
        formatter = LogFormatter(class_length=15)
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="err msg",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert red in result

    def test_format_critical_contains_bold_red(self) -> None:
        """CRITICAL level records use bold red color code."""
        formatter = LogFormatter(class_length=15)
        record = logging.LogRecord(
            name="test",
            level=logging.CRITICAL,
            pathname="",
            lineno=0,
            msg="crit msg",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert bold_red in result

    def test_format_trace_contains_cyan(self) -> None:
        """TRACE level (5) records use cyan color code."""
        formatter = LogFormatter(class_length=15)
        record = logging.LogRecord(
            name="test",
            level=5,
            pathname="",
            lineno=0,
            msg="trace msg",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert cyan in result

    def test_format_truncates_long_name(self) -> None:
        """Names longer than 25 characters are truncated, keeping only the last 25 characters."""
        formatter = LogFormatter(class_length=15)
        long_name = "prefix_" + "suffix" * 5  # 37 chars
        record = logging.LogRecord(
            name=long_name,
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="msg",
            args=(),
            exc_info=None,
        )
        formatter.format(record)
        assert len(record.name) == 15
        assert record.name == long_name[-15:]

    def test_format_short_name_unchanged(self) -> None:
        """Names of 25 characters or fewer are not modified."""
        formatter = LogFormatter(class_length=15)
        short_name = "mylogger"
        record = logging.LogRecord(
            name=short_name,
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="msg",
            args=(),
            exc_info=None,
        )
        formatter.format(record)
        assert record.name == short_name

    def test_format_reset_in_output(self) -> None:
        """Formatted output contains the reset escape code."""
        formatter = LogFormatter(class_length=15)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="msg",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert reset in result


class TestJsonFormatter:
    """Tests for JsonFormatter."""

    def test_format_returns_valid_json(self) -> None:
        """Formatted output is valid JSON."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="testlogger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="hello",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_format_contains_required_fields(self) -> None:
        """JSON output includes timestamp, level, name, and message fields."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="myapp",
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="something happened",
            args=(),
            exc_info=None,
        )
        parsed = json.loads(formatter.format(record))
        assert "timestamp" in parsed
        assert "level" in parsed
        assert "name" in parsed
        assert "message" in parsed

    def test_format_level_name(self) -> None:
        """JSON level field matches the logging level name."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="oops",
            args=(),
            exc_info=None,
        )
        parsed = json.loads(formatter.format(record))
        assert parsed["level"] == "ERROR"

    def test_format_message_content(self) -> None:
        """JSON message field contains the original log message."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="specific message text",
            args=(),
            exc_info=None,
        )
        parsed = json.loads(formatter.format(record))
        assert parsed["message"] == "specific message text"

    def test_format_name_field(self) -> None:
        """JSON name field matches the logger name."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="myservice",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="msg",
            args=(),
            exc_info=None,
        )
        parsed = json.loads(formatter.format(record))
        assert parsed["name"] == "myservice"

    def test_format_extra_data_included(self) -> None:
        """JSON output includes extra field when record has extra_data attribute."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="msg with extra",
            args=(),
            exc_info=None,
        )
        record.extra_data = {"user_id": 42, "action": "login"}
        parsed = json.loads(formatter.format(record))
        assert "extra" in parsed
        assert parsed["extra"] == {"user_id": 42, "action": "login"}

    def test_format_no_extra_data_omits_extra_field(self) -> None:
        """JSON output omits extra field when record has no extra_data attribute."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="plain msg",
            args=(),
            exc_info=None,
        )
        parsed = json.loads(formatter.format(record))
        assert "extra" not in parsed

    def test_format_timestamp_is_iso_format(self) -> None:
        """Timestamp in JSON output is in ISO 8601 format."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="msg",
            args=(),
            exc_info=None,
        )
        parsed = json.loads(formatter.format(record))
        # ISO format contains 'T' separator between date and time
        assert "T" in parsed["timestamp"]


class TestCustomLogger:
    """Tests for CustomLogger."""

    def test_trace_level_value(self) -> None:
        """TRACE level constant equals 5."""
        assert CustomLogger.TRACE == 5

    def test_trace_level_name_registered(self) -> None:
        """TRACE level name is registered with the logging module."""
        assert logging.getLevelName(5) == "TRACE"

    def test_trace_method_logs_at_trace_level(self) -> None:
        """trace() method emits a record at level 5 when logger is enabled for TRACE."""
        logging.setLoggerClass(CustomLogger)
        logger = cast("CustomLogger", logging.getLogger("trace_test_logger"))
        logger.setLevel(CustomLogger.TRACE)

        records: list[logging.LogRecord] = []

        class CapturingHandler(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                records.append(record)

        handler = CapturingHandler()
        logger.addHandler(handler)
        try:
            logger.trace("trace message")
        finally:
            logger.removeHandler(handler)

        assert len(records) == 1
        assert records[0].levelno == 5
        assert records[0].getMessage() == "trace message"

    def test_trace_method_suppressed_when_level_too_high(self) -> None:
        """trace() method does not emit when logger level is above TRACE."""
        logging.setLoggerClass(CustomLogger)
        logger = cast("CustomLogger", logging.getLogger("trace_suppressed_logger"))
        logger.setLevel(logging.DEBUG)

        records: list[logging.LogRecord] = []

        class CapturingHandler(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                records.append(record)

        handler = CapturingHandler()
        logger.addHandler(handler)
        try:
            logger.trace("should not appear")
        finally:
            logger.removeHandler(handler)

        assert len(records) == 0

    def test_setup_logging_creates_log_files(self) -> None:
        """setup_logging() creates the log directory and both log files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            CustomLogger.setup_logging(tmpdir, "testapp", "DEBUG", class_length=15)
            log_dir = Path(tmpdir)
            # JSONL file should be created
            jsonl_file = log_dir / "testapp.jsonl"
            assert jsonl_file.exists(), "JSONL log file was not created"
            # At least one timestamped .log file should be created
            log_files = list(log_dir.glob("testapp-*.log"))
            assert len(log_files) >= 1, "Timestamped .log file was not created"

    def test_setup_logging_creates_directory_if_missing(self) -> None:
        """setup_logging() creates the log directory if it does not exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = str(Path(tmpdir) / "nested" / "logs")
            CustomLogger.setup_logging(nested, "app", "INFO", class_length=15)
            assert Path(nested).is_dir()

    def test_setup_logging_sets_logger_class(self) -> None:
        """After setup_logging(), new loggers are instances of CustomLogger."""
        with tempfile.TemporaryDirectory() as tmpdir:
            CustomLogger.setup_logging(tmpdir, "cls_test", "DEBUG", class_length=15)
            logger = logging.getLogger("brand_new_logger_xyz")
            assert isinstance(logger, CustomLogger)

    def test_setup_logging_jsonl_records_valid_json(self) -> None:
        """Messages logged after setup_logging() produce valid JSON lines in the JSONL file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            CustomLogger.setup_logging(tmpdir, "jsontest", "DEBUG", class_length=15)
            logger = cast("CustomLogger", logging.getLogger("jsontest_logger"))
            logger.info("structured log entry")

            # Flush all handlers
            for handler in logging.getLogger().handlers:
                handler.flush()

            jsonl_path = Path(tmpdir) / "jsontest.jsonl"
            lines = [
                line for line in jsonl_path.read_text().splitlines() if line.strip()
            ]
            assert len(lines) >= 1
            parsed = json.loads(lines[-1])
            assert parsed["message"] == "structured log entry"
