"""Bulk upload companies from Firmenbuch API to Supabase database.

This script supports multiple modes:
1. Import from CSV file containing FNRs or company names
2. Iterate through a range of FNR numbers (e.g., 100000a to 999999z)
3. Single company fetch by FNR

Usage examples:

    # Import from CSV file
    python -m backend.services.ingest.bulk_upload --csv companies.csv

    # Iterate through FNR range
    python -m backend.services.ingest.bulk_upload --range 100000a 200000z

    # Single company
    python -m backend.services.ingest.bulk_upload --fnr 123456a

CSV file format:
    fnr,name
    123456a,Example Company GmbH
    234567b,Another Company AG

Or just FNRs:
    fnr
    123456a
    234567b

Or just names:
    name
    Example Company GmbH
    Another Company AG
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

from backend.services.ingest.api_fetch import (
    FirmenbuchCompanyNotFound,
    FirmenbuchFetchError,
    fetch_company_profile_if_missing,
    fetch_company_profile_by_name_if_missing,
)
from backend.shared.utils import normalize_fn_number, validate_fn_number

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class BulkUploadStats:
    """Track statistics for bulk upload operations."""

    def __init__(self):
        self.total = 0
        self.success = 0
        self.failed = 0
        self.skipped = 0
        self.not_found = 0
        self.start_time = time.time()

    def record_success(self):
        self.success += 1
        self.total += 1

    def record_failure(self):
        self.failed += 1
        self.total += 1

    def record_not_found(self):
        self.not_found += 1
        self.total += 1

    def record_skipped(self):
        self.skipped += 1
        self.total += 1

    def print_progress(self):
        elapsed = time.time() - self.start_time
        rate = self.total / elapsed if elapsed > 0 else 0
        logger.info(
            "Progress: %d total | %d success | %d failed | %d not found | %d skipped | %.2f/sec",
            self.total,
            self.success,
            self.failed,
            self.not_found,
            self.skipped,
            rate,
        )

    def print_summary(self):
        elapsed = time.time() - self.start_time
        logger.info("=" * 60)
        logger.info("BULK UPLOAD SUMMARY")
        logger.info("=" * 60)
        logger.info("Total processed: %d", self.total)
        logger.info("Successful: %d", self.success)
        logger.info("Failed: %d", self.failed)
        logger.info("Not found: %d", self.not_found)
        logger.info("Skipped: %d", self.skipped)
        logger.info("Time elapsed: %.2f seconds", elapsed)
        logger.info("Average rate: %.2f companies/sec", self.total / elapsed if elapsed > 0 else 0)
        logger.info("=" * 60)


def fetch_company_by_fnr(fnr: str, stats: BulkUploadStats, rate_limit: float = 0.5) -> bool:
    """Fetch a single company by FNR and update stats.

    Args:
        fnr: Firmenbuch number
        stats: Statistics tracker
        rate_limit: Minimum seconds between requests (default 0.5 = 2 req/sec)

    Returns:
        True if successful, False otherwise
    """
    try:
        normalized_fnr = normalize_fn_number(fnr)
        logger.info("Fetching company %s...", normalized_fnr)

        result = fetch_company_profile_if_missing(normalized_fnr)
        company_name = result.get("name", "Unknown")

        logger.info("✓ Successfully fetched: %s (%s)", company_name, normalized_fnr)
        stats.record_success()

        # Rate limiting
        time.sleep(rate_limit)
        return True

    except FirmenbuchCompanyNotFound:
        logger.warning("✗ Company not found: %s", fnr)
        stats.record_not_found()
        time.sleep(rate_limit)
        return False

    except FirmenbuchFetchError as exc:
        logger.error("✗ Fetch error for %s: %s", fnr, exc)
        stats.record_failure()
        time.sleep(rate_limit)
        return False

    except Exception as exc:
        logger.exception("✗ Unexpected error for %s: %s", fnr, exc)
        stats.record_failure()
        time.sleep(rate_limit)
        return False


def fetch_company_by_name(name: str, stats: BulkUploadStats, rate_limit: float = 0.5) -> bool:
    """Fetch a company by name and update stats.

    Args:
        name: Company name to search for
        stats: Statistics tracker
        rate_limit: Minimum seconds between requests

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Searching for company: %s...", name)

        result = fetch_company_profile_by_name_if_missing(name)
        fnr = result.get("fnr", "Unknown")

        logger.info("✓ Successfully fetched: %s (%s)", name, fnr)
        stats.record_success()

        time.sleep(rate_limit)
        return True

    except FirmenbuchCompanyNotFound:
        logger.warning("✗ Company not found: %s", name)
        stats.record_not_found()
        time.sleep(rate_limit)
        return False

    except FirmenbuchFetchError as exc:
        logger.error("✗ Fetch error for %s: %s", name, exc)
        stats.record_failure()
        time.sleep(rate_limit)
        return False

    except Exception as exc:
        logger.exception("✗ Unexpected error for %s: %s", name, exc)
        stats.record_failure()
        time.sleep(rate_limit)
        return False


def import_from_csv(
    csv_path: Path,
    rate_limit: float = 0.5,
    progress_interval: int = 10,
) -> BulkUploadStats:
    """Import companies from a CSV file.

    CSV can contain 'fnr' column, 'name' column, or both.

    Args:
        csv_path: Path to CSV file
        rate_limit: Minimum seconds between API requests
        progress_interval: Print progress every N companies

    Returns:
        Statistics object
    """
    stats = BulkUploadStats()

    if not csv_path.exists():
        logger.error("CSV file not found: %s", csv_path)
        return stats

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate CSV structure
        if not reader.fieldnames:
            logger.error("CSV file is empty or invalid")
            return stats

        has_fnr = "fnr" in reader.fieldnames
        has_name = "name" in reader.fieldnames

        if not has_fnr and not has_name:
            logger.error("CSV must contain either 'fnr' or 'name' column")
            return stats

        logger.info("Starting CSV import from: %s", csv_path)
        logger.info("CSV contains: %s", reader.fieldnames)

        for row in reader:
            # Prefer FNR if available, fall back to name
            if has_fnr and row.get("fnr"):
                fnr = row["fnr"].strip()
                if validate_fn_number(fnr):
                    fetch_company_by_fnr(fnr, stats, rate_limit)
                else:
                    logger.warning("Invalid FNR format, skipping: %s", fnr)
                    stats.record_skipped()
            elif has_name and row.get("name"):
                name = row["name"].strip()
                fetch_company_by_name(name, stats, rate_limit)
            else:
                logger.warning("Row missing both fnr and name, skipping: %s", row)
                stats.record_skipped()

            # Print progress
            if stats.total % progress_interval == 0 and stats.total > 0:
                stats.print_progress()

    stats.print_summary()
    return stats


def import_from_fnr_range(
    start_fnr: str,
    end_fnr: str,
    rate_limit: float = 0.5,
    progress_interval: int = 10,
) -> BulkUploadStats:
    """Import companies by iterating through a range of FNR numbers.

    Note: This approach will have many misses since FNR numbers are not sequential.
    Consider using CSV import with known FNRs instead.

    Args:
        start_fnr: Starting FNR (e.g., "100000a")
        end_fnr: Ending FNR (e.g., "200000z")
        rate_limit: Minimum seconds between API requests
        progress_interval: Print progress every N companies

    Returns:
        Statistics object
    """
    stats = BulkUploadStats()

    # Parse start and end FNRs
    start_num, start_check = parse_fnr(start_fnr)
    end_num, end_check = parse_fnr(end_fnr)

    if start_num is None or end_num is None:
        logger.error("Invalid FNR range format. Use format like: 100000a 200000z")
        return stats

    logger.info("Starting FNR range import: %s to %s", start_fnr, end_fnr)
    logger.warning(
        "Note: FNR range iteration will have many misses. "
        "Consider using CSV import with known FNRs."
    )

    # Check characters to iterate through
    check_chars = "abcdefghijklmnopqrstuvwxyz"
    start_check_idx = check_chars.index(start_check.lower()) if start_check else 0
    end_check_idx = check_chars.index(end_check.lower()) if end_check else len(check_chars) - 1

    for num in range(start_num, end_num + 1):
        for check_idx in range(start_check_idx, end_check_idx + 1):
            check_char = check_chars[check_idx]
            fnr = f"{num}{check_char}"

            fetch_company_by_fnr(fnr, stats, rate_limit)

            if stats.total % progress_interval == 0 and stats.total > 0:
                stats.print_progress()

        # Reset check character range for subsequent numbers
        start_check_idx = 0

    stats.print_summary()
    return stats


def parse_fnr(fnr: str) -> Tuple[Optional[int], Optional[str]]:
    """Parse FNR into number and check character.

    Args:
        fnr: FNR string like "123456a"

    Returns:
        Tuple of (number, check_character) or (None, None) if invalid
    """
    import re

    match = re.match(r'^(\d+)([a-zA-Z])?$', fnr.strip())
    if not match:
        return None, None

    number = int(match.group(1))
    check_char = match.group(2) or "a"

    return number, check_char


def main():
    """Main entry point for bulk upload script."""
    parser = argparse.ArgumentParser(
        description="Bulk upload companies from Firmenbuch API to Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Input modes
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--csv",
        type=Path,
        help="Path to CSV file containing FNRs or company names",
    )
    input_group.add_argument(
        "--range",
        nargs=2,
        metavar=("START_FNR", "END_FNR"),
        help="FNR range to iterate through (e.g., 100000a 200000z)",
    )
    input_group.add_argument(
        "--fnr",
        type=str,
        help="Single FNR to fetch",
    )

    # Options
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=0.5,
        help="Minimum seconds between API requests (default: 0.5 = 2 req/sec)",
    )
    parser.add_argument(
        "--progress-interval",
        type=int,
        default=10,
        help="Print progress every N companies (default: 10)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose debug logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Execute based on input mode
    if args.csv:
        import_from_csv(
            args.csv,
            rate_limit=args.rate_limit,
            progress_interval=args.progress_interval,
        )
    elif args.range:
        start_fnr, end_fnr = args.range
        import_from_fnr_range(
            start_fnr,
            end_fnr,
            rate_limit=args.rate_limit,
            progress_interval=args.progress_interval,
        )
    elif args.fnr:
        stats = BulkUploadStats()
        fetch_company_by_fnr(args.fnr, stats, rate_limit=args.rate_limit)
        stats.print_summary()

    return 0


if __name__ == "__main__":
    sys.exit(main())
