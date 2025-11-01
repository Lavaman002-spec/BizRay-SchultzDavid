#!/usr/bin/env python3
"""
Run Bulk API Ingestion Script

This script orchestrates the complete bulk ingestion process:
1. Ensures database schema is ready
2. Discovers and fetches companies from the API
3. Normalizes data into canonical tables
4. Provides detailed progress reporting

Usage:
    python run_bulk_ingest.py [options]
    
Examples:
    # Fetch 100 companies with discovery
    python run_bulk_ingest.py --max 100
    
    # Fetch specific companies
    python run_bulk_ingest.py --companies FN348406 FN10001 FN10002
    
    # Fast ingestion with shorter delay (be careful with rate limits!)
    python run_bulk_ingest.py --max 50 --delay 0.5
    
    # Fetch many companies (will take a while)
    python run_bulk_ingest.py --max 1000 --delay 1.5
"""

import sys
import argparse
from etl.db import ensure_schema, wait_for_db
from etl.bulk_api_ingest import bulk_ingest_from_api
from etl.normalize import run_normalization


def main():
    parser = argparse.ArgumentParser(
        description='Bulk ingest company data from Austrian Business Register API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_bulk_ingest.py --max 100
  python run_bulk_ingest.py --companies FN348406 FN10001
  python run_bulk_ingest.py --max 500 --delay 1.5 --skip-normalize
        """
    )
    
    parser.add_argument(
        '--max', 
        type=int, 
        default=100, 
        help='Maximum number of companies to fetch (default: 100)'
    )
    
    parser.add_argument(
        '--delay', 
        type=float, 
        default=1.0, 
        help='Delay between API requests in seconds (default: 1.0)'
    )
    
    parser.add_argument(
        '--no-discovery', 
        action='store_true', 
        help='Skip discovery phase, use sample companies instead'
    )
    
    parser.add_argument(
        '--companies', 
        nargs='+', 
        help='Specific company register IDs to fetch (e.g., FN348406 FN10001)'
    )
    
    parser.add_argument(
        '--skip-normalize', 
        action='store_true', 
        help='Skip normalization step (only ingest to staging tables)'
    )
    
    parser.add_argument(
        '--skip-schema-check', 
        action='store_true', 
        help='Skip database schema initialization check'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🚀 BizRay Bulk API Ingestion Tool")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  Max Companies:     {args.max}")
    print(f"  Request Delay:     {args.delay}s")
    print(f"  Use Discovery:     {not args.no_discovery}")
    print(f"  Normalize Data:    {not args.skip_normalize}")
    print(f"  Specific Companies: {args.companies if args.companies else 'None'}")
    print()
    
    try:
        # Step 1: Ensure database is ready
        if not args.skip_schema_check:
            print("\n[Step 1/3] Checking database connection...")
            wait_for_db()
            
            print("[Step 1/3] Ensuring database schema...")
            ensure_schema()
        else:
            print("\n[Step 1/3] Skipping schema check (as requested)")
        
        # Step 2: Run bulk ingestion
        print("\n[Step 2/3] Running bulk API ingestion...")
        stats = bulk_ingest_from_api(
            company_list=args.companies,
            max_companies=args.max,
            delay_between_requests=args.delay,
            use_discovery=not args.no_discovery
        )
        
        # Step 3: Normalize data
        if not args.skip_normalize and stats['successful'] > 0:
            print("\n[Step 3/3] Normalizing data into canonical tables...")
            run_normalization()
            print("✅ Normalization complete!")
        elif args.skip_normalize:
            print("\n[Step 3/3] Skipping normalization (as requested)")
        else:
            print("\n[Step 3/3] No data to normalize (no successful fetches)")
        
        # Final summary
        print("\n" + "=" * 80)
        print("✅ BULK INGESTION PIPELINE COMPLETE")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   Companies Fetched: {stats['successful']}/{stats['total_attempted']}")
        if 'duration_seconds' in stats:
            print(f"   Total Time: {stats['duration_seconds']/60:.2f} minutes")
        
        if stats['failed'] > 0:
            print(f"\n⚠️  Note: {stats['failed']} companies failed to fetch")
            print("   Check logs above for details")
        
        print("\n🎉 You can now query the data using the BizRay API!")
        print("   Example: http://localhost:8080/api/companies/search?q=company_name")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        print("   Partial data may have been ingested")
        return 130
        
    except Exception as e:
        print(f"\n\n❌ Error during bulk ingestion: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
