#!/usr/bin/env python3
"""
Search and Fetch CLI Tool

Usage:
    python search_company.py "erste"
    python search_company.py "Aalborg" --no-fetch
    python search_company.py "SIGNA" --max-fetch 3
"""

import argparse
import sys
from etl.search_and_fetch import search_and_fetch, interactive_search_and_fetch


def main():
    parser = argparse.ArgumentParser(
        description='Search for companies and fetch from API if not found',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python search_company.py "erste"
  python search_company.py "Aalborg" --no-fetch
  python search_company.py "SIGNA" --max-fetch 3
  python search_company.py --interactive
        """
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        help='Company name to search for'
    )
    
    parser.add_argument(
        '--no-fetch',
        action='store_true',
        help='Do not fetch from API if not found locally'
    )
    
    parser.add_argument(
        '--max-results',
        type=int,
        default=5,
        help='Maximum API search results to consider (default: 5)'
    )
    
    parser.add_argument(
        '--max-fetch',
        type=int,
        default=1,
        help='Maximum companies to fetch from API (default: 1)'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive:
        interactive_search_and_fetch()
        return 0
    
    # Non-interactive mode requires query
    if not args.query:
        parser.print_help()
        print("\n⚠️  Error: Please provide a search query or use --interactive")
        return 1
    
    print("=" * 80)
    print("🔍 Company Search and Fetch Tool")
    print("=" * 80)
    
    result = search_and_fetch(
        query=args.query,
        fetch_if_not_found=not args.no_fetch,
        max_api_results=args.max_results,
        max_to_fetch=args.max_fetch
    )
    
    # Display results
    print("\n" + "=" * 80)
    print("📋 RESULTS")
    print("=" * 80)
    
    if result['local_results']:
        print(f"\n✅ Found {len(result['local_results'])} companies in database:")
        for i, company in enumerate(result['local_results'], 1):
            print(f"\n  {i}. {company['name']}")
            print(f"     Register ID: {company['register_id']}")
            print(f"     City: {company.get('city', 'N/A')}")
            print(f"     Legal Form: {company.get('legal_form', 'N/A')}")
            print(f"     Status: {company.get('status', 'N/A')}")
    elif result['api_results']:
        print(f"\n📡 Found {len(result['api_results'])} companies in API (not in database):")
        for i, company in enumerate(result['api_results'][:10], 1):
            print(f"  {i}. FNR: {company['fnr']}")
            print(f"     Name: {company.get('firma', 'N/A')}")
    else:
        print("\n❌ No results found")
        print(f"   Query: '{args.query}'")
        print("   Searched: Local database and API")
    
    if result['fetched']:
        print(f"\n⬇️  FETCHED AND STORED:")
        for company in result['fetched']:
            print(f"  ✓ {company['name']} ({company['fnr']})")
    
    print("\n" + "=" * 80)
    print("\n💡 Tips:")
    print("  - Search results are cached in the database")
    print("  - Use --no-fetch to skip API search")
    print("  - Use --interactive for continuous searching")
    print("  - API URL: http://localhost:8080/api/companies/search?q=erste&fetch_if_not_found=true")
    print()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
