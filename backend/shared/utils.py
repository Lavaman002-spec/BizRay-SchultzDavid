"""Utility functions for the backend."""
from typing import Optional, Dict, Any
import re


def normalize_fn_number(fn_number: str) -> str:
    """
    Normalize Firmenbuch number to standard format.
    
    Args:
        fn_number: Raw FN number string
        
    Returns:
        Normalized FN number
    """
    # Remove whitespace and convert to uppercase
    normalized = fn_number.strip().upper()
    
    # Remove 'FN' prefix if present
    if normalized.startswith('FN'):
        normalized = normalized[2:].strip()
    
    return normalized


def validate_fn_number(fn_number: str) -> bool:
    """
    Validate Firmenbuch number format.
    
    Args:
        fn_number: FN number to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Austrian FN numbers typically follow pattern: 123456a or FN 123456a
    pattern = r'^(FN\s?)?\d{4,8}[a-z]?$'
    return bool(re.match(pattern, fn_number.strip(), re.IGNORECASE))


def format_company_name(name: str) -> str:
    """
    Format company name for consistency.
    
    Args:
        name: Raw company name
        
    Returns:
        Formatted company name
    """
    return name.strip()


def parse_address(address: Optional[str]) -> Dict[str, Optional[str]]:
    """
    Parse address string into components.
    
    Args:
        address: Full address string
        
    Returns:
        Dictionary with address components
    """
    if not address:
        return {
            "street": None,
            "city": None,
            "postal_code": None,
            "country": None
        }
    
    # Basic parsing - can be enhanced based on actual address formats
    parts = address.split(',')
    
    result = {
        "street": parts[0].strip() if len(parts) > 0 else None,
        "city": parts[1].strip() if len(parts) > 1 else None,
        "postal_code": None,
        "country": "Austria"
    }
    
    # Try to extract postal code from city part
    if result["city"]:
        postal_match = re.match(r'(\d{4})\s+(.+)', result["city"])
        if postal_match:
            result["postal_code"] = postal_match.group(1)
            result["city"] = postal_match.group(2)
    
    return result


def sanitize_input(text: str, max_length: int = 255) -> str:
    """
    Sanitize user input.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove leading/trailing whitespace
    sanitized = text.strip()
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized
