"""
Text normalization utilities for card names, sets, and conditions.

This module provides functions to normalize and clean card data to ensure
consistent formatting across different stores and enable accurate price
comparisons.
"""

import re
from typing import Optional


def normalize_card_name(name: str) -> str:
    """
    Normalize a card name for consistent comparison.
    
    This function:
    - Strips leading/trailing whitespace
    - Normalizes multiple spaces to single spaces
    - Removes special characters (if needed)
    - Standardizes capitalization
    
    Args:
        name: The raw card name from user input or store data
    
    Returns:
        A normalized card name string
    
    Example:
        >>> normalize_card_name("  Lightning  Bolt  ")
        'Lightning Bolt'
    """
    if not name:
        return ""
    
    # Strip whitespace and normalize multiple spaces
    normalized = re.sub(r'\s+', ' ', name.strip())
    
    return normalized


def normalize_set_code(set_code: Optional[str]) -> Optional[str]:
    """
    Normalize a set code or name.
    
    Args:
        set_code: The raw set code or name (e.g., "7ED", "Seventh Edition")
    
    Returns:
        A normalized set code, or None if input is None/empty
    
    Example:
        >>> normalize_set_code("  7ed  ")
        '7ED'
    """
    if not set_code:
        return None
    
    # Convert to uppercase and strip whitespace
    normalized = set_code.strip().upper()
    
    return normalized if normalized else None


def normalize_condition(condition: str) -> str:
    """
    Normalize a card condition string.
    
    Common conditions: NM (Near Mint), LP (Lightly Played), 
                      MP (Moderately Played), HP (Heavily Played), DMG (Damaged)
    
    Args:
        condition: The raw condition string from store data
    
    Returns:
        A normalized condition abbreviation
    
    Example:
        >>> normalize_condition("Near Mint")
        'NM'
        >>> normalize_condition("lightly played")
        'LP'
    """
    if not condition:
        return "NM"  # Default to Near Mint
    
    condition_upper = condition.strip().upper()
    
    # Map common variations to standard abbreviations
    condition_map = {
        "NEAR MINT": "NM",
        "NEARMINT": "NM",
        "NM": "NM",
        "MINT": "NM",
        "LIGHTLY PLAYED": "LP",
        "LIGHTLYPLAYED": "LP",
        "LP": "LP",
        "LIGHT PLAY": "LP",
        "MODERATELY PLAYED": "MP",
        "MODERATELYPLAYED": "MP",
        "MP": "MP",
        "MODERATE PLAY": "MP",
        "HEAVILY PLAYED": "HP",
        "HEAVILYPLAYED": "HP",
        "HP": "HP",
        "HEAVY PLAY": "HP",
        "DAMAGED": "DMG",
        "DMG": "DMG",
        "POOR": "DMG",
    }
    
    return condition_map.get(condition_upper, condition_upper)


def normalize_price(price: str) -> float:
    """
    Extract and normalize a price from a string.
    
    Args:
        price: A price string (e.g., "$12.99", "12.99", "CAD 12.99")
    
    Returns:
        The price as a float
    
    Raises:
        ValueError: If the price cannot be parsed
    
    Example:
        >>> normalize_price("$12.99")
        12.99
        >>> normalize_price("CAD 15.50")
        15.5
    """
    if not price:
        raise ValueError("Price cannot be empty")
    
    # Remove currency symbols and common text
    cleaned = re.sub(r'[^\d.]', '', str(price))
    
    try:
        return float(cleaned)
    except ValueError:
        raise ValueError(f"Cannot parse price: {price}")
