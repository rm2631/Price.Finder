"""
Abstract base class for store scrapers.

This module defines the StoreScraper interface that all store-specific
scrapers must implement to ensure consistency across different stores.
"""

from abc import ABC, abstractmethod
from typing import List
from mtg_deal_finder.cards import Card, Offer


class StoreScraper(ABC):
    """
    Abstract base class for MTG card store scrapers.
    
    All store-specific scrapers must inherit from this class and implement
    the search method to provide a consistent interface for searching cards
    across different stores.
    """
    
    @abstractmethod
    def search(self, card: Card) -> List[Offer]:
        """
        Search for a card in the store and return available offers.
        
        Args:
            card: A Card object containing the card name, set, and quantity
        
        Returns:
            A list of Offer objects representing available offers for the card.
            Returns an empty list if no offers are found.
        
        Raises:
            Exception: Implementation-specific exceptions may be raised for
                      network errors, parsing errors, etc.
        """
        pass
