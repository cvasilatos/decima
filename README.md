# Decima

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Decima** is a robust, custom logging library for Python that enhances your application's observability with colorful console output and structured JSON logging. Designed for clarity and ease of use, it helps developers track down issues faster with a dedicated `TRACE` level and automatic file management.

## Key Features

- **🎨 Colorful Console Output**: Instantly distinguish log levels with vibrant color coding (Cyan for TRACE, Blue for DEBUG, Red for ERROR, etc.).
- **📊 Structured JSON Logging**: Automatically writes logs to `.jsonl` files, perfect for ingestion by log analysis tools.
- **🔍 Custom TRACE Level**: Includes a `TRACE` (level 5) severity for ultra-granular debugging, below the standard `DEBUG`.
- **📁 Automated File Management**: seamlessly handles log file creation, including timestamped run logs and cumulative JSON logs.
- **⚡ Simple Configuration**: Get up and running with a single static setup call.

## Installation

Decima is a Python library. Since it is not yet on PyPI, you can install it directly from the git repository using `pip` or `uv`:

```bash
# Using pip
pip install "git+https://github.com/cvasilatos/decima.git"

# Using uv
uv add "git+https://github.com/cvasilatos/decima.git"
```

*(Note: Adjust installation command based on your package registry status. If running locally, ensure you build and install the wheel.)*

## Usage

Integrating Decima into your project is straightforward.

### 1. Setup Logging

Initialize the logger at the start of your application entry point:

```python
import logging
from typing import cast

from decima import CustomLogger

# Configure logging:
# - folder: Directory to store log files
# - filename: Base name for log files
# - level: Minimum logging level (e.g., "DEBUG", "INFO")
# - class_length: Max length for logger name in console output (for alignment)
CustomLogger.setup_logging(
    folder="logs",
    filename="app",
    level="DEBUG",
    class_length=20
)

# Get a typed logger instance inside your class
class MyApp:
    def __init__(self) -> None:
        self.logger: CustomLogger = cast(
            "CustomLogger",
            logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}"),
        )
```

### 2. Logging Messages

You can now use the standard logging methods, plus the `trace` method:

```python
app = MyApp()
app.logger.info("Application started successfully.")
app.logger.warning("Configuration file missing, using defaults.")
app.logger.error("Failed to connect to database.")
app.logger.trace("Entering complex calculation loop...")
```

## Output Formats

**Console Output:**
```text
2023-10-27 10:00:00,123 - [INFO] - MyApp - Application started successfully.
```
*(With appropriate colors applied)*

**JSON Output (`logs/app.jsonl`):**
```json
{"timestamp": "2023-10-27T10:00:00.123456-05:00", "level": "INFO", "name": "MyApp", "message": "Application started successfully."}
```

## specific Configuration

- **`LogFormatter`**: Handles the colorization and formatting of console logs.
- **`JsonFormatter`**: Handles the serialization of log records into JSON structure.
- **`class_length`**: Truncates the logger name in the console output to keep columns aligned, preserving the end of the name.

## Development

This project uses `uv` for dependency management and `hatch` for building.

### Setting up the environment

```bash
uv sync --all-extras --dev
```

### Running Tests

```bash
uv run pytest
```

### Linting & Formatting

```bash
uv run ruff check .
uv run ruff format .
```

### Building Documentation

Decima uses `mkdocs` for documentation.

```bash
uv run mkdocs serve
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
