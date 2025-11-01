#!/usr/bin/env python3
"""
Example: How to use the bulk API ingestion module

This file demonstrates various ways to use the bulk ingestion functionality.
"""

# Example 1: Simple bulk ingestion with defaults
def example_basic():
    """Basic example: Fetch 50 companies with discovery"""
    from etl.bulk_api_ingest import bulk_ingest_from_api
    from etl.normalize import run_normalization
    
    print("Example 1: Basic Bulk Ingestion")
    print("=" * 60)
    
    # Fetch companies
    stats = bulk_ingest_from_api(
        max_companies=50,
        delay_between_requests=1.0,
        use_discovery=True
    )
    
    # Normalize the data
    if stats['successful'] > 0:
        print("\nNormalizing data...")
        run_normalization()
    
    print(f"\nComplete! Fetched {stats['successful']} companies")


# Example 2: Fetch specific companies
def example_specific_companies():
    """Example: Fetch a predefined list of companies"""
    from etl.bulk_api_ingest import bulk_ingest_from_api
    from etl.normalize import run_normalization
    
    print("Example 2: Specific Companies")
    print("=" * 60)
    
    # List of companies to fetch
    companies = [
        "FN348406",  # Example Austrian company
        "FN10001",
        "FN10002",
        "FN10003",
    ]
    
    stats = bulk_ingest_from_api(
        company_list=companies,
        delay_between_requests=1.0
    )
    
    if stats['successful'] > 0:
        run_normalization()
    
    print(f"\nComplete! Fetched {stats['successful']}/{len(companies)} companies")


# Example 3: Fast ingestion (use with caution)
def example_fast_ingestion():
    """Example: Fast ingestion with shorter delays (test only!)"""
    from etl.bulk_api_ingest import bulk_ingest_from_api
    
    print("Example 3: Fast Ingestion (Testing)")
    print("=" * 60)
    print("⚠️  Warning: Short delays may hit rate limits!")
    
    stats = bulk_ingest_from_api(
        max_companies=10,
        delay_between_requests=0.3,  # Very short delay - use only for testing!
        use_discovery=False  # Use sample companies
    )
    
    print(f"\nComplete! Fetched {stats['successful']} companies in {stats['duration_seconds']:.1f}s")


# Example 4: Custom discovery strategy
def example_custom_discovery():
    """Example: Discover companies first, then fetch with custom logic"""
    from etl.bulk_api_ingest import bulk_search_companies, bulk_ingest_from_api
    from etl.normalize import run_normalization
    
    print("Example 4: Custom Discovery Strategy")
    print("=" * 60)
    
    # Phase 1: Discover companies
    print("\n[Phase 1] Discovering companies...")
    discovered_companies = bulk_search_companies(
        max_companies=200,
        delay_between_requests=0.5
    )
    
    print(f"Discovered {len(discovered_companies)} companies")
    
    # Phase 2: Filter or process the list
    # For example, only fetch the first 50
    selected_companies = discovered_companies[:50]
    print(f"Selected {len(selected_companies)} companies to fetch")
    
    # Phase 3: Fetch detailed data
    print("\n[Phase 2] Fetching detailed data...")
    stats = bulk_ingest_from_api(
        company_list=selected_companies,
        delay_between_requests=1.0
    )
    
    # Phase 4: Normalize
    if stats['successful'] > 0:
        print("\n[Phase 3] Normalizing data...")
        run_normalization()
    
    print(f"\nComplete! Fetched {stats['successful']}/{len(selected_companies)} companies")


# Example 5: Incremental ingestion
def example_incremental():
    """Example: Check what's already ingested and fetch new data"""
    from etl.bulk_api_ingest import bulk_ingest_from_api, _is_already_ingested
    from etl.normalize import run_normalization
    
    print("Example 5: Incremental Ingestion")
    print("=" * 60)
    
    # List of companies we want to have
    target_companies = [
        "FN348406",
        "FN10001",
        "FN10002",
        "FN10003",
        "FN10004",
        "FN10005",
    ]
    
    # Check which ones are already in the database
    new_companies = []
    existing_companies = []
    
    for company_id in target_companies:
        if _is_already_ingested(company_id):
            existing_companies.append(company_id)
        else:
            new_companies.append(company_id)
    
    print(f"Already in database: {len(existing_companies)}")
    print(f"Need to fetch: {len(new_companies)}")
    
    if new_companies:
        print(f"\nFetching {len(new_companies)} new companies...")
        stats = bulk_ingest_from_api(
            company_list=new_companies,
            delay_between_requests=1.0
        )
        
        if stats['successful'] > 0:
            run_normalization()
        
        print(f"\nComplete! Added {stats['successful']} new companies")
    else:
        print("\nAll companies already in database!")


# Example 6: Batch processing with progress
def example_batch_processing():
    """Example: Process companies in batches"""
    from etl.bulk_api_ingest import bulk_ingest_from_api
    from etl.normalize import run_normalization
    import time
    
    print("Example 6: Batch Processing")
    print("=" * 60)
    
    # Generate a larger list of company IDs (example)
    all_companies = [f"FN{i:05d}" for i in range(10001, 10101)]  # 100 companies
    batch_size = 25
    
    total_successful = 0
    
    # Process in batches
    for i in range(0, len(all_companies), batch_size):
        batch = all_companies[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(all_companies) + batch_size - 1) // batch_size
        
        print(f"\n{'='*60}")
        print(f"Processing Batch {batch_num}/{total_batches}")
        print(f"Companies: {batch[0]} to {batch[-1]}")
        print(f"{'='*60}")
        
        stats = bulk_ingest_from_api(
            company_list=batch,
            delay_between_requests=1.0
        )
        
        total_successful += stats['successful']
        
        # Normalize after each batch
        if stats['successful'] > 0:
            print(f"\nNormalizing batch {batch_num}...")
            run_normalization()
        
        # Small break between batches
        if i + batch_size < len(all_companies):
            print("\nCooling down for 5 seconds before next batch...")
            time.sleep(5)
    
    print(f"\n{'='*60}")
    print(f"Batch Processing Complete!")
    print(f"Total successful: {total_successful}/{len(all_companies)}")
    print(f"{'='*60}")


# Example 7: Query results after ingestion
def example_query_results():
    """Example: Query and display ingested data"""
    from etl.db import get_connection
    
    print("Example 7: Query Ingested Data")
    print("=" * 60)
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Count companies
    cur.execute("SELECT COUNT(*) FROM companies")
    company_count = cur.fetchone()[0]
    print(f"\nTotal companies: {company_count}")
    
    # Count officers
    cur.execute("SELECT COUNT(*) FROM officers")
    officer_count = cur.fetchone()[0]
    print(f"Total officers: {officer_count}")
    
    # Show recent companies
    print("\nRecent companies:")
    cur.execute("""
        SELECT register_id, name, city, created_at 
        FROM companies 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} ({row[2]})")
    
    # Show companies with most officers
    print("\nCompanies with most officers:")
    cur.execute("""
        SELECT c.register_id, c.name, COUNT(o.id) as officer_count
        FROM companies c
        LEFT JOIN officers o ON c.id = o.company_id
        GROUP BY c.id, c.register_id, c.name
        ORDER BY officer_count DESC
        LIMIT 5
    """)
    
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} - {row[2]} officers")
    
    cur.close()
    conn.close()


# Main menu
def main():
    """Interactive menu to run examples"""
    examples = {
        '1': ('Basic bulk ingestion (50 companies)', example_basic),
        '2': ('Fetch specific companies', example_specific_companies),
        '3': ('Fast ingestion (testing)', example_fast_ingestion),
        '4': ('Custom discovery strategy', example_custom_discovery),
        '5': ('Incremental ingestion', example_incremental),
        '6': ('Batch processing', example_batch_processing),
        '7': ('Query results', example_query_results),
    }
    
    print("=" * 60)
    print("Bulk API Ingestion - Examples")
    print("=" * 60)
    print("\nAvailable examples:")
    for key, (description, _) in examples.items():
        print(f"  {key}. {description}")
    print("  q. Quit")
    print()
    
    choice = input("Select an example (1-7 or q): ").strip()
    
    if choice.lower() == 'q':
        print("Goodbye!")
        return
    
    if choice in examples:
        _, func = examples[choice]
        print()
        try:
            func()
        except KeyboardInterrupt:
            print("\n\n⚠️  Example interrupted by user")
        except Exception as e:
            print(f"\n❌ Error running example: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"Invalid choice: {choice}")


if __name__ == "__main__":
    main()
