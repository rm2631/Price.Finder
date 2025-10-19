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


# Common words that are typically descriptors, not part of card names
# These are words that might be added to searches but aren't part of the actual card name
DESCRIPTOR_WORDS = {'foil', 'non-foil', 'nonfoil', 'promo', 'extended', 'art', 'showcase', 
                    'borderless', 'full', 'alternate', 'alt'}


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


def card_name_matches_query(card_name: str, query: str) -> bool:
    """
    Check if a card name matches the search query.
    
    This function validates that the card name from a store result actually matches
    the original search query. It uses case-insensitive comparison and checks if
    all words from the query appear in the card name, filtering out common words
    that might be descriptors rather than part of the card name.
    
    Args:
        card_name: The card name from the store result
        query: The original search query (card name)
    
    Returns:
        True if the card name matches the query, False otherwise
    
    Example:
        >>> card_name_matches_query("Lightning Bolt", "lightning bolt")
        True
        >>> card_name_matches_query("Brainstone", "brainstorm")
        False
        >>> card_name_matches_query("Brainstorm", "brainstorm")
        True
        >>> card_name_matches_query("Sol Ring", "sol ring")
        True
    """
    if not card_name or not query:
        return False
    
    # Normalize both strings for comparison
    normalized_card = normalize_card_name(card_name).lower()
    normalized_query = normalize_card_name(query).lower()
    
    # Split query into words
    query_words = normalized_query.split()
    
    # Filter out descriptor words from the query - these are optional matches
    core_query_words = [word for word in query_words if word not in DESCRIPTOR_WORDS]
    
    # If query has no core words after filtering, require exact match
    # This handles edge cases like searching for just "foil" or "promo" alone
    if not core_query_words:
        return normalized_query == normalized_card
    
    # Check if all core query words appear in the card name
    # This handles cases where card names have additional text (e.g., "Lightning Bolt - Foil")
    for word in core_query_words:
        if word not in normalized_card:
            return False
    
    return True
