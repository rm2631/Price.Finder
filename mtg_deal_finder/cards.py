"""
Data models for MTG cards and store offers.

This module defines the core data structures used throughout the application:
- Card: Represents a Magic: The Gathering card to be searched
- Offer: Represents a card offer from a specific store
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Card:
    """
    Represents a Magic: The Gathering card to be searched.
    
    Attributes:
        name: The name of the card (e.g., "Lightning Bolt")
        set: The set code or name (optional, e.g., "M11" or "Magic 2011")
        qty: The quantity needed (default: 1)
    """
    name: str
    set: Optional[str] = None
    qty: int = 1
    
    def __post_init__(self):
        """Validate card data after initialization."""
        if not self.name:
            raise ValueError("Card name cannot be empty")
        if self.qty < 1:
            raise ValueError("Quantity must be at least 1")


@dataclass
class Offer:
    """
    Represents a card offer from a specific store.
    
    Attributes:
        store: The name of the store (e.g., "FaceToFace")
        card: The card name as listed by the store
        set: The set code or name
        condition: The card condition (e.g., "NM", "LP", "MP")
        price: The price in CAD
        url: The direct URL to the product page
        foil: Whether the card is foil (default: False)
        availability: Whether the card is in stock (default: True)
        query: The original search query that generated this offer (default: "")
    """
    store: str
    card: str
    set: str
    condition: str
    price: float
    url: str
    foil: bool = False
    availability: bool = True
    query: str = ""
    
    def __post_init__(self):
        """Validate offer data after initialization."""
        if not self.store:
            raise ValueError("Store name cannot be empty")
        if not self.card:
            raise ValueError("Card name cannot be empty")
        if self.price < 0:
            raise ValueError("Price cannot be negative")
