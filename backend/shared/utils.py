"""Utility functions for the backend."""
from typing import Optional, Dict, Any
import re


def normalize_fn_number(fn_number: str) -> str:
    # Remove whitespace
    normalized = fn_number.strip()

    # Remove 'FN' prefix if present (case-insensitive)
    if normalized.upper().startswith('FN'):
        normalized = normalized[2:].strip()

    # Remove leading zeros from numeric part
    # Austrian FNR format: up to 6 digits + lowercase check character
    match = re.match(r'^0*(\d+)([a-zA-Z])$', normalized)
    if match:
        digits = match.group(1)
        check_char = match.group(2).lower()  # Check character should be lowercase
        normalized = f"{digits}{check_char}"
    else:
        # If no check character, just keep as is
        normalized = normalized.lstrip('0')

    return normalized


def validate_fn_number(fn_number: str) -> bool:
    # Austrian FN numbers typically follow pattern: 123456a or FN 123456a
    pattern = r'^(FN\s?)?\d{4,8}[a-z]?$'
    return bool(re.match(pattern, fn_number.strip(), re.IGNORECASE))


def format_company_name(name: str) -> str:
    return name.strip()


def parse_address(address: Optional[str]) -> Dict[str, Optional[str]]:
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
