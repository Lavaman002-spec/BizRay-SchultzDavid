"""
Bulk API Ingestion Module

This module fetches company data in bulk from the Austrian Business Register API
using various search strategies to maximize data collection.
"""

import sys
import os
import time
import json
from datetime import date, datetime
from typing import List, Dict, Optional
from zeep.helpers import serialize_object

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from client import create_client
from db import get_connection
from api_fetch import DateTimeEncoder, fetch_company


def bulk_search_companies(
    max_companies: int = 1000,
    delay_between_requests: float = 0.5
) -> List[str]:
    """
    Perform bulk search to discover company register IDs using SUCHEFIRMA API.
    
    Based on actual API response examples, searches by:
    - Legal form (GES = GmbH is most common)
    - City codes (ORTNR)
    - Wildcard searches
    
    Args:
        max_companies: Maximum number of companies to discover
        delay_between_requests: Delay in seconds between API calls
        
    Returns:
        List of unique company register IDs (FNR)
    """
    client = create_client()
    discovered_fnrs = set()
    
    print(f"🔍 Starting bulk company discovery (target: {max_companies} companies)")
    
    # Austrian city codes (ORTNR) for major cities
    cities = [
        ("90001", "Wien"),
        ("60101", "Graz"),
        ("40101", "Linz"),
        ("50101", "Salzburg"),
        ("70101", "Innsbruck"),
        ("20101", "Klagenfurt"),
        ("80227", "Bregenz"),
        ("40301", "Wels"),
        ("31701", "St. Pölten"),
    ]
    
    # Most common legal forms in Austria
    legal_forms = ["GES", "AG", "KEG"]  # GmbH, AG, KG
    
    for rechtsform in legal_forms:
        if len(discovered_fnrs) >= max_companies:
            break
            
        for ortnr, city_name in cities:
            if len(discovered_fnrs) >= max_companies:
                break
                
            try:
                print(f"  → Searching {rechtsform} in {city_name}...")
                
                # Use correct SUCHEFIRMA parameters based on API examples
                params = {
                    "FIRMENWORTLAUT": "*",  # Wildcard for all companies
                    "EXAKTESUCHE": False,
                    "SUCHBEREICH": 1,  # 1 = normal search
                    "GERICHT": "",     # Empty = all courts
                    "RECHTSFORM": rechtsform,
                    "RECHTSEIGENSCHAFT": "",
                    "ORTNR": ortnr
                }
                
                resp = client.service.SUCHEFIRMA(**params)
                result = serialize_object(resp)
                
                if result and result.get('ERGEBNIS'):
                    new_companies = 0
                    for company in result['ERGEBNIS']:
                        if isinstance(company, dict):
                            fnr = company.get('FNR', '')
                            if fnr and fnr not in discovered_fnrs:
                                # SUCHEFIRMA returns FNRs without space (e.g., "348406m")
                                # but AUSZUG_V2_ requires them with space (e.g., "348406 m")
                                # Convert format: add space before last character if not already present
                                if ' ' not in fnr and len(fnr) > 1:
                                    fnr = fnr[:-1] + ' ' + fnr[-1]
                                
                                discovered_fnrs.add(fnr)
                                new_companies += 1
                    
                    print(f"    ✓ Found {new_companies} new companies ({len(discovered_fnrs)} total)")
                else:
                    print(f"    ⚠️  No results")
                
                time.sleep(delay_between_requests)
                
            except Exception as e:
                print(f"    ⚠️ Error: {str(e)[:100]}")
                continue
    
    print(f"\n📊 Discovery complete: Found {len(discovered_fnrs)} unique companies")
    return list(discovered_fnrs)[:max_companies]


def bulk_search_by_fnr_range(
    start_fnr: int = 1,
    end_fnr: int = 100000,
    sample_rate: int = 100,
    delay_between_requests: float = 0.5
) -> List[str]:
    """
    Search for companies by FNR number range.
    
    This samples company register numbers within a range to discover valid companies.
    Austrian FNRs can be quite large, so we sample strategically.
    
    Args:
        start_fnr: Starting FNR number
        end_fnr: Ending FNR number
        sample_rate: Check every Nth FNR (default: 100)
        delay_between_requests: Delay in seconds between API calls
        
    Returns:
        List of valid company register IDs
    """
    client = create_client()
    valid_fnrs = []
    
    print(f"🔢 Searching FNR range {start_fnr} to {end_fnr} (sample rate: 1 in {sample_rate})")
    
    for fnr_num in range(start_fnr, end_fnr, sample_rate):
        fnr = f"{fnr_num}m"  # Austrian FNRs often end with 'm'
        
        try:
            # Use SUCHEURKUNDE to check if company exists
            resp = client.service.SUCHEURKUNDE(FNR=str(fnr_num))
            result = serialize_object(resp)
            
            if result and result.get('ERGEBNIS'):
                valid_fnrs.append(fnr)
                print(f"  ✓ Found valid company: FN{fnr_num}")
            
            time.sleep(delay_between_requests)
            
            # Progress indicator
            if fnr_num % (sample_rate * 10) == 0:
                print(f"  ... Progress: {fnr_num}/{end_fnr} ({len(valid_fnrs)} found)")
            
        except Exception as e:
            # Most errors will be "company not found" which is expected
            if "404" not in str(e).lower() and "not found" not in str(e).lower():
                print(f"  ⚠️ Error checking FN{fnr_num}: {e}")
            continue
    
    print(f"\n📊 Range search complete: Found {len(valid_fnrs)} valid companies")
    return valid_fnrs


def bulk_ingest_from_api(
    company_list: Optional[List[str]] = None,
    max_companies: int = 1000,
    delay_between_requests: float = 1.0,
    use_discovery: bool = True
):
    """
    Bulk ingest company data from the Austrian Business Register API.
    
    This function:
    1. Discovers company IDs (if company_list not provided)
    2. Fetches detailed data for each company
    3. Stores data in staging tables
    4. Provides progress tracking and error handling
    
    Args:
        company_list: Optional list of specific company register IDs to fetch
        max_companies: Maximum number of companies to fetch
        delay_between_requests: Delay in seconds between API requests (rate limiting)
        use_discovery: If True and company_list is None, discover companies first
        
    Returns:
        dict with statistics about the ingestion process
    """
    print("=" * 70)
    print("🚀 BULK API INGESTION - Austrian Business Register")
    print("=" * 70)
    
    stats = {
        'total_attempted': 0,
        'successful': 0,
        'failed': 0,
        'skipped': 0,
        'start_time': time.time()
    }
    
    # Step 1: Get list of companies to fetch
    if company_list is None:
        if use_discovery:
            print("\n[Phase 1] Discovering companies...")
            company_list = bulk_search_companies(
                max_companies=max_companies,
                delay_between_requests=delay_between_requests
            )
        else:
            # Use a predefined sample of known companies
            print("\n[Phase 1] Using predefined company sample...")
            company_list = _get_sample_companies(max_companies)
    
    if not company_list:
        print("❌ No companies to fetch. Exiting.")
        stats['end_time'] = time.time()
        stats['duration_seconds'] = stats['end_time'] - stats['start_time']
        return stats
    
    # Limit to max_companies
    company_list = company_list[:max_companies]
    stats['total_attempted'] = len(company_list)
    
    print(f"\n[Phase 2] Fetching detailed data for {len(company_list)} companies...")
    print(f"           Rate limit: {delay_between_requests}s between requests")
    print(f"           Estimated time: {len(company_list) * delay_between_requests / 60:.1f} minutes")
    
    # Step 2: Fetch detailed data for each company
    for idx, company_id in enumerate(company_list, 1):
        try:
            print(f"\n[{idx}/{len(company_list)}] Fetching {company_id}...")
            
            # Check if already ingested
            if _is_already_ingested(company_id):
                print(f"  ⏭️  Already in database, skipping")
                stats['skipped'] += 1
                continue
            
            # Fetch company data
            company_data = fetch_company(company_id)
            
            if company_data:
                stats['successful'] += 1
                print(f"  ✅ Success: {company_data.get('name', 'Unknown')}")
            else:
                stats['failed'] += 1
                print(f"  ⚠️  No data returned")
            
            # Rate limiting
            time.sleep(delay_between_requests)
            
            # Progress checkpoint every 10 companies
            if idx % 10 == 0:
                elapsed = time.time() - stats['start_time']
                rate = idx / elapsed
                remaining = len(company_list) - idx
                eta_seconds = remaining / rate if rate > 0 else 0
                
                print(f"\n📊 Progress Checkpoint:")
                print(f"   Completed: {idx}/{len(company_list)} ({idx/len(company_list)*100:.1f}%)")
                print(f"   Success: {stats['successful']}, Failed: {stats['failed']}, Skipped: {stats['skipped']}")
                print(f"   Rate: {rate:.2f} companies/second")
                print(f"   ETA: {eta_seconds/60:.1f} minutes")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Ingestion interrupted by user")
            break
            
        except Exception as e:
            stats['failed'] += 1
            print(f"  ❌ Error: {e}")
            # Continue with next company
            continue
    
    # Final statistics
    stats['end_time'] = time.time()
    stats['duration_seconds'] = stats['end_time'] - stats['start_time']
    
    _print_final_stats(stats)
    
    return stats


def _get_sample_companies(max_count: int = 100) -> List[str]:
    """
    Get a predefined sample of known Austrian companies.
    
    Austrian FNRs have a specific format: up to 6 digits + SPACE + check character
    Example: "348406 m", "10001 a", "50234 m", etc.
    
    IMPORTANT: Based on actual API responses, the format is "NNNNNN m" (with space!)
    
    Args:
        max_count: Maximum number of companies to return
        
    Returns:
        List of company register IDs
    """
    sample_companies = []
    
    # Most common check character is 'm', but we'll use a variety
    # Note: From API examples, 'm' is most common
    check_chars = ['m', 'a', 'b', 'v', 'w', 'x', 'y', 'z', 't', 'h', 'd', 'f']
    
    # Generate FNRs across different ranges (max 6 digits = 999999)
    # We'll sample strategically across ranges more likely to have companies
    ranges = [
        (1, 1000, 10),          # Very early registrations (every 10th)  
        (1000, 10000, 50),      # Early companies (every 50th)
        (10000, 50000, 100),    # Growing phase (every 100th)
        (50000, 100000, 200),   # Expansion (every 200th)
        (100000, 200000, 300),  # Mid-range (every 300th)
        (200000, 400000, 500),  # Higher range (every 500th)
        (400000, 600000, 800),  # Recent registrations (every 800th)
    ]
    
    char_index = 0
    for start, end, step in ranges:
        if len(sample_companies) >= max_count:
            break
        
        for fnr_num in range(start, min(end, 1000000), step):  # Max 6 digits = 999999
            if len(sample_companies) >= max_count:
                break
            
            # Ensure we don't exceed 6 digits
            if fnr_num > 999999:
                break
                
            # Add check character (use 'm' more frequently as it's most common)
            if char_index % 3 == 0:  # Every 3rd uses 'm'
                check_char = 'm'
            else:
                check_char = check_chars[char_index % len(check_chars)]
            
            # IMPORTANT: Add space before check character (this is the correct format!)
            fnr = f"{fnr_num} {check_char}"
            sample_companies.append(fnr)
            char_index += 1
    
    return sample_companies[:max_count]


def _is_already_ingested(register_id: str) -> bool:
    """
    Check if a company has already been ingested into staging.
    
    Args:
        register_id: Company register ID to check
        
    Returns:
        True if company exists in stg_companies, False otherwise
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Normalize register_id (remove FN prefix if present)
        normalized_id = register_id.replace("FN", "").strip()
        
        cur.execute("""
            SELECT COUNT(*) FROM stg_companies 
            WHERE register_id = %s OR register_id = %s
        """, (register_id, normalized_id))
        
        count = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return count > 0
        
    except Exception as e:
        print(f"⚠️ Error checking if company exists: {e}")
        return False


def _print_final_stats(stats: Dict):
    """
    Print final ingestion statistics.
    
    Args:
        stats: Dictionary containing ingestion statistics
    """
    print("\n" + "=" * 70)
    print("📊 BULK INGESTION COMPLETE")
    print("=" * 70)
    print(f"\n🎯 Results:")
    print(f"   Total Attempted:  {stats['total_attempted']}")
    print(f"   ✅ Successful:     {stats['successful']}")
    print(f"   ❌ Failed:         {stats['failed']}")
    print(f"   ⏭️  Skipped:        {stats['skipped']}")
    print(f"\n⏱️  Duration: {stats['duration_seconds']/60:.2f} minutes")
    
    if stats['total_attempted'] > 0:
        success_rate = (stats['successful'] / stats['total_attempted']) * 100
        print(f"   Success Rate: {success_rate:.1f}%")
    
    if stats['successful'] > 0:
        avg_time = stats['duration_seconds'] / stats['successful']
        print(f"   Avg Time per Company: {avg_time:.2f} seconds")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    """
    Run bulk ingestion when script is executed directly.
    
    Usage:
        python -m backend.services.ingest.etl.bulk_api_ingest
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Bulk ingest company data from Austrian Business Register API')
    parser.add_argument('--max', type=int, default=100, help='Maximum number of companies to fetch')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests (seconds)')
    parser.add_argument('--no-discovery', action='store_true', help='Skip discovery phase, use sample companies')
    parser.add_argument('--companies', nargs='+', help='Specific company IDs to fetch')
    
    args = parser.parse_args()
    
    bulk_ingest_from_api(
        company_list=args.companies,
        max_companies=args.max,
        delay_between_requests=args.delay,
        use_discovery=not args.no_discovery
    )
