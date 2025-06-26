"""Script to download 10-K filings for all S&P 500 companies."""

import asyncio
import time
from collections.abc import Coroutine
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles
import httpx
import pandas as pd
import structlog

# Configure structlog for the script
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.make_filtering_bound_logger(min_level="info"),
)

log = structlog.get_logger()


class Sp500TenKDownloader:
    """Downloads 10-K filings for S&P 500 companies from the SEC EDGAR database."""

    CONCURRENCY_LIMIT = 10

    def __init__(
        self: "Sp500TenKDownloader",
        download_dir: str = "data/pdfs",
        user_agent: str = "Your Company Name yourname@yourcompany.com",
    ) -> None:
        """Initializes the downloader.

        Args:
            download_dir: The directory where filings will be saved.
            user_agent: The User-Agent header for SEC requests.
                        The SEC requires a User-Agent header.
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.user_agent = user_agent
        self.log = log.bind(class_name=self.__class__.__name__)
        self._ticker_data: dict[str, Any] | None = None

    async def get_sp500_companies(self: "Sp500TenKDownloader") -> list[dict[str, str]]:
        """Get current S&P 500 company list from Wikipedia.

        Returns:
            A list of dictionaries, where each dictionary represents a company.
        """
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        self.log.info("Fetching S&P 500 company list", url=url)

        try:
            # pd.read_html is synchronous, run in a thread to avoid blocking event loop
            tables = await asyncio.to_thread(pd.read_html, url, flavor="lxml")
            sp500_table = tables[0]  # First table contains the companies

            # Extract company info
            companies = [
                {
                    "symbol": row["Symbol"],
                    "company_name": row["Security"],
                    "sector": row["GICS Sector"],
                    "industry": row["GICS Sub-Industry"],
                }
                for _, row in sp500_table.iterrows()
            ]

            self.log.info(
                "Successfully fetched S&P 500 company list",
                company_count=len(companies),
            )
            return companies

        except (ValueError, IndexError, KeyError) as e:
            self.log.error(
                "Error parsing S&P 500 page. It may have changed.",
                error=str(e),
                url=url,
            )
            return []

    async def _get_ticker_data(
        self: "Sp500TenKDownloader", client: httpx.AsyncClient
    ) -> dict[str, Any] | None:
        """Fetch and cache the SEC company ticker data."""
        if self._ticker_data is None:
            tickers_url = "https://www.sec.gov/files/company_tickers.json"
            try:
                response = await client.get(tickers_url)
                response.raise_for_status()
                self._ticker_data = response.json()
            except httpx.HTTPStatusError as e:
                self.log.error(
                    "HTTP error fetching company tickers",
                    status_code=e.response.status_code,
                    error=str(e),
                    url=tickers_url,
                )
                return None
            except httpx.RequestError as e:
                self.log.error(
                    "Error fetching company tickers", error=str(e), url=tickers_url
                )
                return None
        return self._ticker_data

    async def get_company_cik(self: "Sp500TenKDownloader", symbol: str) -> str | None:
        """Get CIK (Central Index Key) for a company symbol from cached data.

        Args:
            symbol: The company's stock symbol.

        Returns:
            The company's CIK as a string, or None if not found.
        """
        if not self._ticker_data:
            self.log.error("Ticker data not loaded. Cannot find CIK.")
            return None

        for _, company in self._ticker_data.items():
            if company["ticker"] == symbol:
                cik = str(company["cik_str"]).zfill(10)
                self.log.debug("Found CIK for symbol", symbol=symbol, cik=cik)
                return cik
        self.log.warning("CIK for symbol not found", symbol=symbol)
        return None

    async def get_company_filings(
        self: "Sp500TenKDownloader", client: httpx.AsyncClient, cik: str
    ) -> dict[str, Any] | None:
        """Get all filings for a company by CIK.

        Args:
            client: The httpx client to use for the request.
            cik: The company's CIK.

        Returns:
            A dictionary containing the company's filings data, or None on error.
        """
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"

        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            self.log.error(
                "HTTP error fetching filings for CIK",
                cik=cik,
                status_code=e.response.status_code,
                error=str(e),
            )
        except httpx.RequestError as e:
            self.log.error(
                "Error fetching filings for CIK",
                cik=cik,
                error=str(e),
                status_code=e.response.status_code if hasattr(e, "response") else None,  # type: ignore
            )

        return None

    def filter_10k_filings(
        self: "Sp500TenKDownloader", filings_data: dict[str, Any]
    ) -> list[dict[str, str]]:
        """Filter for 10-K filings from company data.

        Args:
            filings_data: The raw filings data from the SEC.

        Returns:
            A list of 10-K filings.
        """
        if "filings" not in filings_data or "recent" not in filings_data["filings"]:
            self.log.warning("No recent filings found in data")
            return []

        filings = filings_data["filings"]["recent"]
        filtered_filings = []

        for i, form_type in enumerate(filings.get("form", [])):
            # Include all 10-K variants
            if form_type in ["10-K", "10-K/A", "10-KT", "10-KT/A"]:
                filing = {
                    "accession_number": filings["accessionNumber"][i],
                    "filing_date": filings["filingDate"][i],
                    "form_type": form_type,
                    "file_number": filings.get("fileNumber", [""])[i],
                    "primary_document": filings.get("primaryDocument", [""])[i],
                }
                filtered_filings.append(filing)

        return filtered_filings

    async def download_filing(
        self: "Sp500TenKDownloader",
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        cik: str,
        accession_number: str,
        company_symbol: str,
        filing_date: str,
        form_type: str,
    ) -> bool:
        """Download individual 10-K filing.

        Args:
            client: The httpx client to use for the request.
            semaphore: The semaphore to limit concurrent downloads.
            cik: Company CIK.
            accession_number: The filing's accession number.
            company_symbol: The company's stock symbol.
            filing_date: The date the filing was submitted.
            form_type: The type of the form (e.g., '10-K').

        Returns:
            True if download was successful, False otherwise.
        """
        # Clean accession number for URL
        clean_accession = accession_number.replace("-", "")

        # Construct EDGAR URL
        url = (
            f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
            f"{clean_accession}/{accession_number}.txt"
        )

        async with semaphore:
            try:
                response = await client.get(url)
                response.raise_for_status()

                # Create company directory
                company_dir = self.download_dir / company_symbol
                company_dir.mkdir(exist_ok=True)

                # Sanitize form_type for filename
                safe_form_type = form_type.replace("/", "_")

                # Save filing
                filename = (
                    f"{company_symbol}_{safe_form_type}_{filing_date}_"
                    f"{accession_number}.txt"
                )
                filepath = company_dir / filename

                # Use async file I/O
                async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
                    await f.write(response.text)

                self.log.info("Downloaded filing", filename=filename)
                return True

            except httpx.HTTPStatusError as e:
                self.log.error(
                    "Failed to download filing due to HTTP error",
                    symbol=company_symbol,
                    form_type=form_type,
                    date=filing_date,
                    status_code=e.response.status_code,
                    error=str(e),
                )
                return False
            except httpx.RequestError as e:
                status_code = "Unknown"
                if hasattr(e, "response") and e.response:
                    status_code = e.response.status_code  # type: ignore
                self.log.error(
                    "Failed to download filing",
                    symbol=company_symbol,
                    form_type=form_type,
                    date=filing_date,
                    status_code=status_code,
                    error=str(e),
                )
                return False

            except OSError as e:
                self.log.error(
                    "Error saving filing to disk",
                    symbol=company_symbol,
                    form_type=form_type,
                    error=str(e),
                )
                return False

    async def download_all_sp500_10k(
        self: "Sp500TenKDownloader", years_back: int = 5
    ) -> None:
        """Download all 10-K filings for S&P 500 companies.

        Args:
            years_back: How many years of filings to download.
        """
        main_log = self.log.bind(years_back=years_back)
        start_time = time.monotonic()

        headers = {"User-Agent": self.user_agent}
        async with httpx.AsyncClient(
            headers=headers, timeout=30.0, follow_redirects=True
        ) as client:
            # Pre-fetch all company and ticker data
            companies = await self.get_sp500_companies()
            if not companies:
                main_log.error("Could not fetch S&P 500 company list. Aborting.")
                return

            if await self._get_ticker_data(client) is None:
                main_log.error("Could not fetch company ticker data. Aborting.")
                return

            # Calculate date threshold
            cutoff_year = datetime.now().year - years_back

            main_log.info(
                "Starting download of 10-K filings",
                total_companies=len(companies),
                cutoff_year=cutoff_year,
            )

            # Step 1: Gather all filings to be downloaded
            filings_to_download = []
            for i, company in enumerate(companies):
                symbol = company["symbol"]
                company_log = main_log.bind(
                    company_symbol=symbol,
                    company_name=company["company_name"],
                    progress=f"{i+1}/{len(companies)}",
                )
                company_log.info("Checking company for filings")

                cik = await self.get_company_cik(symbol)
                if not cik:
                    company_log.warning("Could not find CIK for company")
                    continue

                filings_data = await self.get_company_filings(client, cik)
                if not filings_data:
                    company_log.warning("Could not fetch filings for company")
                    continue

                filings_10k = self.filter_10k_filings(filings_data)
                recent_filings = [
                    f for f in filings_10k if int(f["filing_date"][:4]) >= cutoff_year
                ]

                if not recent_filings:
                    company_log.info("No recent 10-K filings found")
                    continue

                company_log.info("Found recent 10-K filings", count=len(recent_filings))

                for filing in recent_filings:
                    filings_to_download.append(
                        {
                            "cik": cik,
                            "symbol": symbol,
                            "accession_number": filing["accession_number"],
                            "filing_date": filing["filing_date"],
                            "form_type": filing["form_type"],
                        }
                    )

            # Step 2: Download all filings concurrently
            main_log.info(
                "Starting concurrent download of all filings",
                total_filings=len(filings_to_download),
            )
            semaphore = asyncio.Semaphore(
                self.CONCURRENCY_LIMIT
            )  # Limit to 10 concurrent requests
            download_tasks: list[Coroutine[Any, Any, bool]] = []
            for filing_info in filings_to_download:
                task = self.download_filing(
                    client,
                    semaphore,
                    filing_info["cik"],
                    filing_info["accession_number"],
                    filing_info["symbol"],
                    filing_info["filing_date"],
                    filing_info["form_type"],
                )
                download_tasks.append(task)

            results = await asyncio.gather(*download_tasks)

        # Summary
        successful_downloads = sum(1 for r in results if r)
        total_downloads = len(results)
        end_time = time.monotonic()

        summary_log = main_log.bind(
            total_companies=len(companies),
            total_filings_found=total_downloads,
            successful_downloads=successful_downloads,
            failed_downloads=total_downloads - successful_downloads,
            duration_seconds=f"{end_time - start_time:.2f}",
        )
        summary_log.info("Download summary")

        # Create a human-readable summary for console output if needed
        human_readable_summary = (
            "\n=== DOWNLOAD SUMMARY ===\n"
            f"Total companies processed: {len(companies)}\n"
            f"Total filings found: {total_downloads}\n"
            f"Successfully downloaded: {successful_downloads}\n"
            f"Failed downloads: {total_downloads - successful_downloads}\n"
            f"Total time: {end_time - start_time:.2f} seconds\n"
            f"All files saved to: {self.download_dir.absolute()}\n"
        )
        summary_log.info(human_readable_summary)


# Usage example
async def main() -> None:
    """Main function to run the downloader."""
    # Initialize downloader
    # The SEC requires you to declare a user agent.
    # Replace with your own details.
    downloader = Sp500TenKDownloader(
        download_dir="data/pdfs", user_agent="Your Name username@domain.com"
    )

    # Download all S&P 500 10-K filings from the last 3 years
    await downloader.download_all_sp500_10k(years_back=3)


if __name__ == "__main__":
    asyncio.run(main())
