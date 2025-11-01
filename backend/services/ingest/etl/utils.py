def normalize_register_id(register_id: str) -> str:
    """
    Normalize a company register ID to a consistent format.
    
    Args:
        register_id: Raw register ID (e.g., "FN 348406 m", "348406m")
    
    Returns:
        Normalized register ID (e.g., "348406M")
    """
    if not register_id:
        return ""
    
    # Remove common prefixes
    normalized = register_id.strip().upper()
    normalized = normalized.replace("FN", "").replace(" ", "")
    
    return normalized


def safe_get(dictionary: dict, *keys, default=None):
    """
    Safely navigate nested dictionaries.
    
    Args:
        dictionary: The dictionary to navigate
        *keys: Sequence of keys to navigate
        default: Default value if key path doesn't exist
    
    Returns:
        The value at the key path, or default if not found
    
    Example:
        safe_get(data, 'company', 'address', 'city', default='Unknown')
    """
    current = dictionary
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current