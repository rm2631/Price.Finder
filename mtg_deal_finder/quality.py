"""
Quality/Condition ranking system for MTG cards.

This module provides a standardized ranking system for card conditions,
allowing users to filter cards based on minimum quality requirements.
"""

from enum import IntEnum
from typing import Optional


class CardQuality(IntEnum):
    """
    Enumeration of card quality levels, ranked from best to worst.
    
    The integer values represent the quality ranking, where higher values
    indicate better condition. This allows for easy comparison using
    standard comparison operators.
    """
    DAMAGED = 1
    HEAVILY_PLAYED = 2
    PLAYED = 3
    MODERATELY_PLAYED = 4
    LIGHTLY_PLAYED = 5
    NEAR_MINT = 6
    MINT = 7
    
    @classmethod
    def from_string(cls, condition: str) -> Optional['CardQuality']:
        """
        Convert a condition string to a CardQuality enum value.
        
        This method handles various common condition name formats and abbreviations.
        
        Args:
            condition: The condition string (e.g., "Near Mint", "NM", "LP")
        
        Returns:
            The corresponding CardQuality enum value, or None if not recognized
        """
        if not condition:
            return None
        
        # Normalize the condition string
        condition_lower = condition.lower().strip()
        
        # Map various condition formats to CardQuality values
        condition_map = {
            # Full names
            'mint': cls.MINT,
            'm': cls.MINT,
            'near mint': cls.NEAR_MINT,
            'nm': cls.NEAR_MINT,
            'lightly played': cls.LIGHTLY_PLAYED,
            'lp': cls.LIGHTLY_PLAYED,
            'moderately played': cls.MODERATELY_PLAYED,
            'mp': cls.MODERATELY_PLAYED,
            'played': cls.PLAYED,
            'pl': cls.PLAYED,
            'p': cls.PLAYED,
            'heavily played': cls.HEAVILY_PLAYED,
            'hp': cls.HEAVILY_PLAYED,
            'damaged': cls.DAMAGED,
            'dmg': cls.DAMAGED,
        }
        
        return condition_map.get(condition_lower)
    
    def to_display_name(self) -> str:
        """
        Get the human-readable display name for this quality level.
        
        Returns:
            A formatted string representation of the quality level
        """
        display_names = {
            CardQuality.MINT: "Mint",
            CardQuality.NEAR_MINT: "Near Mint",
            CardQuality.LIGHTLY_PLAYED: "Lightly Played",
            CardQuality.MODERATELY_PLAYED: "Moderately Played",
            CardQuality.PLAYED: "Played",
            CardQuality.HEAVILY_PLAYED: "Heavily Played",
            CardQuality.DAMAGED: "Damaged",
        }
        return display_names.get(self, "Unknown")


# Available quality options for CLI help text
QUALITY_OPTIONS = ["mint", "nm", "lp", "mp", "played", "hp", "damaged"]


def meets_minimum_quality(condition: str, min_quality: Optional[CardQuality]) -> bool:
    """
    Check if a card condition meets the minimum quality requirement.
    
    Args:
        condition: The condition string of the card offer
        min_quality: The minimum required quality level, or None for no restriction
    
    Returns:
        True if the condition meets or exceeds the minimum quality, False otherwise.
        If min_quality is None, always returns True.
        If condition cannot be parsed, returns False.
    """
    if min_quality is None:
        return True
    
    card_quality = CardQuality.from_string(condition)
    if card_quality is None:
        # Unknown condition - be conservative and reject it
        return False
    
    return card_quality >= min_quality
