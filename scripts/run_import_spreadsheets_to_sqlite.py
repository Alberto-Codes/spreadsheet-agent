#!/usr/bin/env python3
"""Import CSVs to a local SQLite database for debugging.

This script discovers all CSV files in the `data/spreadsheets` directory
and imports each one into a separate table in a SQLite database located at
`data/dbs/local_debug.sqlite3`.

"""

import argparse
import re
import sqlite3
import sys
import traceback
from pathlib import Path
from types import TracebackType

import pandas as pd
import structlog

LOG_FILE = Path(__file__).parent / "import_spreadsheets_to_sqlite.log"


class FileLogger:
    """Structlog processor to log events to a file in JSON format."""

    def __init__(self: "FileLogger", file_path: Path) -> None:
        """Initialize the file logger with the given file path."""
        self._file = None
        self.file_path = file_path

    def __enter__(self: "FileLogger") -> "FileLogger":
        """Open the log file."""
        self._file = open(self.file_path, "a", encoding="utf-8")
        return self

    def __exit__(
        self: "FileLogger",
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close the log file."""
        if self._file:
            self._file.close()

    def __call__(
        self: "FileLogger",
        logger: structlog.BoundLogger,
        method_name: str,
        event_dict: dict,
    ) -> dict:
        """Write the event dict as JSON to the log file."""
        if self._file is None:
            msg = "FileLogger is not used as a context manager."
            raise TypeError(msg)
        rendered = structlog.processors.JSONRenderer()(logger, method_name, event_dict)
        self._file.write(str(rendered) + "\n")
        self._file.flush()
        return event_dict


def sanitize_table_name(name: str) -> str:
    """Sanitize a string to a valid and safe SQLite table name."""
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if sanitized and sanitized[0].isdigit():
        sanitized = f"_{sanitized}"
    return sanitized


def ensure_directories(
    input_dir: Path,
    output_dir: Path,
    logger: structlog.BoundLogger,
) -> None:
    """Ensure input and output directories exist."""
    if not input_dir.exists():
        logger.error("Input directory does not exist", input_dir=str(input_dir))
        sys.exit(1)
    output_dir.mkdir(parents=True, exist_ok=True)


def discover_spreadsheet_files(
    input_dir: Path,
    logger: structlog.BoundLogger,
) -> list[Path]:
    """Return a list of spreadsheet files in the input directory."""
    extensions = ["*.csv", "*.xlsx", "*.xls"]
    files = []
    for ext in extensions:
        files.extend(input_dir.glob(ext))
    logger.info("Discovered spreadsheet files", files=[str(f) for f in files])
    return files


def import_spreadsheet_to_sqlite(
    file_path: Path,
    conn: sqlite3.Connection,
    logger: structlog.BoundLogger,
) -> str | None:
    """Import a spreadsheet into a SQLite table."""
    ext = file_path.suffix.lower()
    if ext == ".csv":
        return import_csv_to_sqlite(file_path, conn, logger, on_bad_lines="skip")
    if ext in [".xlsx", ".xls"]:
        return import_excel_to_sqlite(file_path, conn, logger)
    logger.warning("Unsupported file type", file=file_path.name)
    return None


def import_excel_to_sqlite(
    excel_path: Path,
    conn: sqlite3.Connection,
    logger: structlog.BoundLogger,
) -> str | None:
    """Import an Excel sheet into a SQLite table. Imports the first sheet."""
    try:
        df = pd.read_excel(excel_path, sheet_name=0)
        table_name = sanitize_table_name(excel_path.stem)
        df.to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False,
        )
        msg = "Imported Excel sheet as table"
        row_count = len(df)
        log_args = {
            "file": excel_path.name,
            "sheet": 0,
            "table": table_name,
            "row_count": row_count,
        }
        logger.info(msg, **log_args)
        return table_name
    except (pd.errors.ParserError, ValueError, OSError, sqlite3.DatabaseError) as e:
        msg = "Failed to import Excel sheet"
        tb_str = traceback.format_exc()
        log_args = {
            "file": excel_path.name,
            "error": str(e),
            "exc_info": True,
            "traceback": tb_str,
        }
        logger.error(msg, **log_args)
        return None


def import_csv_to_sqlite(
    csv_path: Path,
    conn: sqlite3.Connection,
    logger: structlog.BoundLogger,
    on_bad_lines: str | None = None,
) -> str | None:
    """Import a CSV into a SQLite table with a dynamic schema.

    Args:
        csv_path: Path to the CSV file.
        conn: SQLite connection object.
        logger: Logger for structured logging.
        on_bad_lines: Policy for handling bad lines in the CSV file.
            Defaults to None.

    Returns:
        The sanitized table name if successful, otherwise None.
    """
    try:
        df = pd.read_csv(csv_path, on_bad_lines=on_bad_lines)
        table_name = sanitize_table_name(csv_path.stem)
        df.to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False,
        )
        msg = "Imported CSV as table"
        row_count = len(df)
        log_args = {
            "file": csv_path.name,
            "table": table_name,
            "row_count": row_count,
        }
        logger.info(msg, **log_args)  # noqa: E501
        return table_name
    except (pd.errors.ParserError, OSError, sqlite3.DatabaseError) as e:
        msg = "Failed to import CSV"
        tb_str = traceback.format_exc()
        log_args = {
            "file": csv_path.name,
            "error": str(e),
            "exc_info": True,
            "traceback": tb_str,
        }
        logger.error(msg, **log_args)  # noqa: E501
        return None


def validate_import(
    conn: sqlite3.Connection,
    table_names: list[str],
    logger: structlog.BoundLogger,
) -> None:
    """Perform basic validation: row counts and schema inventory."""
    for table in table_names:
        try:
            # Table names are sanitized, so double quotes are safe
            cur = conn.execute(
                f'SELECT COUNT(*) FROM "{table}"'  # noqa: S608
            )
            row_count = cur.fetchone()[0]
            logger.info(
                "Validated table",
                table=table,
                row_count=row_count,
            )
        except sqlite3.DatabaseError as e:
            logger.warning(
                "Validation failed for table",
                table=table,
                error=str(e),
            )


def main() -> None:
    """Import all spreadsheets in the input directory into SQLite tables."""
    with FileLogger(LOG_FILE) as file_logger:
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.format_exc_info,
                file_logger,
            ]
        )
        logger = structlog.get_logger()

        parser = argparse.ArgumentParser(
            description="Import spreadsheets into SQLite for local debugging."
        )
        parser.add_argument(
            "--input-dir",
            type=Path,
            default=Path("data/spreadsheets"),
            help="The directory to scan for spreadsheet files.",
        )
        parser.add_argument(
            "--db-path",
            type=Path,
            default=Path("data/dbs") / "local_debug.sqlite3",
            help="The path to the SQLite database file.",
        )
        args = parser.parse_args()

        ensure_directories(args.input_dir, args.db_path.parent, logger)
        spreadsheet_files = discover_spreadsheet_files(args.input_dir, logger)
        if not spreadsheet_files:
            logger.info("No spreadsheet files found in input directory.")
            return

        with sqlite3.connect(args.db_path) as conn:
            imported_tables: list[str] = []
            for file_path in spreadsheet_files:
                logger.info("Processing spreadsheet file", file=file_path.name)
                table_name = import_spreadsheet_to_sqlite(file_path, conn, logger)
                if table_name:
                    imported_tables.append(table_name)
                else:
                    logger.warning(
                        "Skipped file due to import error",
                        file=file_path.name,
                    )
            validate_import(conn, imported_tables, logger)


if __name__ == "__main__":
    main()
