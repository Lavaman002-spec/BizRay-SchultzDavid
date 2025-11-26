import sys
from pathlib import Path
import re
import logging

# Add backend to path
BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.database.client import get_supabase_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_encoding(text: str) -> str:
    """Fix common encoding artifacts."""
    if not text:
        return text
    
    replacements = {
        'Ã¼': 'ü',
        'Ã4': 'Ä',
        'Ã¶': 'ö',
        'ÃŸ': 'ß',
        'Ã©': 'é',
        'Ã ': 'à',
        'Ã¨': 'è',
        # Add more as discovered
    }
    
    for bad, good in replacements.items():
        text = text.replace(bad, good)
        
    return text

def parse_address(address_str: str) -> dict:
    """Parse address string into components."""
    # Simple heuristic parsing
    # Format often: Street 123, 1010 Vienna
    
    parts = {}
    if not address_str:
        return parts
        
    # Try to extract Zip and City
    # Regex for "1234 CityName" at end of string
    match = re.search(r'(\d{4})\s+(.+)$', address_str)
    if match:
        parts['postal_code'] = match.group(1)
        parts['city'] = match.group(2)
        # Remove zip/city from rest
        street_part = address_str[:match.start()].strip().rstrip(',')
        parts['street'] = street_part
    else:
        parts['street'] = address_str
        
    return parts

def clean_data():
    client = get_supabase_client()
    
    logger.info("Fetching companies...")
    # Fetch in chunks in real life, but here we fetch all for simplicity or limit
    response = client.table('companies').select('*').limit(1000).execute()
    companies = response.data
    
    updated_count = 0
    
    for company in companies:
        original_name = company.get('name', '')
        fixed_name = fix_encoding(original_name)
        
        updates = {}
        if fixed_name != original_name:
            updates['name'] = fixed_name
            
        # Check address (assuming address is in company table or linked)
        # If address is in company table as string 'address'
        if 'address' in company and company['address']:
            original_addr = company['address']
            fixed_addr = fix_encoding(original_addr)
            if fixed_addr != original_addr:
                updates['address'] = fixed_addr
                
            # Also parse if needed, but usually we update specific address columns
            # If we have 'street', 'city' columns in companies table
            if 'street' in company:
                 parsed = parse_address(fixed_addr)
                 if parsed.get('street') and parsed['street'] != company.get('street'):
                     updates['street'] = parsed['street']
                 if parsed.get('city') and parsed['city'] != company.get('city'):
                     updates['city'] = parsed['city']
                 if parsed.get('postal_code') and parsed['postal_code'] != company.get('postal_code'):
                     updates['postal_code'] = parsed['postal_code']

        if updates:
            logger.info(f"Updating company {company['id']}: {updates}")
            client.table('companies').update(updates).eq('id', company['id']).execute()
            updated_count += 1
            
    logger.info(f"Finished. Updated {updated_count} companies.")

if __name__ == "__main__":
    clean_data()
