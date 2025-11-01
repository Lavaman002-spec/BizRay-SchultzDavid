"""
Test script for API ingestion functionality.
Run this to verify that the ETL pipeline works correctly.

Usage:
    python test_ingestion.py [company_id]
    
Examples:
    python test_ingestion.py FN348406
    python test_ingestion.py  # Uses default test companies
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from etl.etl_main import run_etl


def main():
    """Run ETL with test companies."""
    
    # Get company ID from command line or use defaults
    if len(sys.argv) > 1:
        test_companies = sys.argv[1:]
        print(f"Testing with companies: {test_companies}")
    else:
        test_companies = None  # Use defaults
        print("Testing with default sample companies")
    
    try:
        print("\n" + "="*60)
        print("BizRay API Ingestion Test")
        print("="*60 + "\n")
        
        run_etl(sample_companies=test_companies)
        
        print("\n✅ Test completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())