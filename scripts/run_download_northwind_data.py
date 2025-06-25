"""Script to download Northwind CSV files.

Downloads orders.csv and order-details.csv from the Neo4j dataset, ensuring the
data directory exists, logging progress, and validating the final files.
"""

from pathlib import Path

import httpx
import structlog

logger = structlog.get_logger()

NORTHWIND_BASE_URL = "https://data.neo4j.com/northwind/"
FILES = [
    "orders.csv",
    "order-details.csv",
]
DATA_DIR = Path("data/spreadsheets")


def ensure_data_dir_exists() -> None:
    """Ensure the data directory exists, creating it if necessary."""
    if not DATA_DIR.exists():
        logger.info("Creating data directory", path=str(DATA_DIR))
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    else:
        logger.info("Data directory already exists", path=str(DATA_DIR))


def download_file(filename: str) -> None:
    """Download a file from the Northwind dataset and save it to the data directory.

    Args:
        filename: The name of the file to download.
    """
    url = f"{NORTHWIND_BASE_URL}{filename}"
    dest = DATA_DIR / filename
    logger.info("Starting download", url=url, dest=str(dest))
    try:
        with httpx.stream("GET", url) as response:
            response.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
        logger.info("Download complete", file=str(dest), size=dest.stat().st_size)
    except Exception as e:
        logger.error("Download failed", url=url, error=str(e))
        raise


def validate_files() -> None:
    """Validate that all required files exist and are not empty in the data directory.

    Raises:
        FileNotFoundError: If any file is missing or empty.
    """
    for filename in FILES:
        dest = DATA_DIR / filename
        if dest.exists() and dest.stat().st_size > 0:
            logger.info("File validated", file=str(dest), size=dest.stat().st_size)
        else:
            logger.error("File missing or empty", file=str(dest))
            raise FileNotFoundError(f"{dest} is missing or empty.")


def main() -> None:
    """Run the full Northwind CSV download and validation workflow."""
    ensure_data_dir_exists()
    for filename in FILES:
        download_file(filename)
    validate_files()
    logger.info("All files downloaded and validated.")


if __name__ == "__main__":
    main()
