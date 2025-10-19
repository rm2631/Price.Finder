"""
Selection strategies for choosing the best card offer.

This module provides different strategies for selecting the best card offer
from a list of available offers. Strategies include cheapest, cheapest foil,
cheapest non-foil, blingiest (most expensive foil), etc.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from mtg_deal_finder.cards import Offer


class SelectionStrategy(ABC):
    """
    Abstract base class for card selection strategies.
    
    All selection strategies must inherit from this class and implement
    the select method to provide a consistent interface.
    """
    
    @abstractmethod
    def select(self, offers: List[Offer]) -> Optional[Offer]:
        """
        Select the best offer based on the strategy.
        
        Args:
            offers: A list of Offer objects to choose from
        
        Returns:
            The selected Offer object, or None if no suitable offer is found
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of the strategy.
        
        Returns:
            A human-readable name for the strategy
        """
        pass


class CheapestStrategy(SelectionStrategy):
    """
    Strategy that selects the cheapest available offer regardless of condition or foil status.
    """
    
    def select(self, offers: List[Offer]) -> Optional[Offer]:
        """
        Select the cheapest offer from the list.
        
        Args:
            offers: A list of Offer objects
        
        Returns:
            The cheapest offer, or None if the list is empty
        """
        if not offers:
            return None
        
        # Filter only available offers
        available_offers = [o for o in offers if o.availability]
        
        if not available_offers:
            return None
        
        return min(available_offers, key=lambda x: x.price)
    
    def get_name(self) -> str:
        return "Cheapest"


class CheapestFoilStrategy(SelectionStrategy):
    """
    Strategy that selects the cheapest foil card.
    """
    
    def select(self, offers: List[Offer]) -> Optional[Offer]:
        """
        Select the cheapest foil offer from the list.
        
        Args:
            offers: A list of Offer objects
        
        Returns:
            The cheapest foil offer, or None if no foil offers are available
        """
        if not offers:
            return None
        
        # Filter for available foil offers
        foil_offers = [o for o in offers if o.foil and o.availability]
        
        if not foil_offers:
            return None
        
        return min(foil_offers, key=lambda x: x.price)
    
    def get_name(self) -> str:
        return "Cheapest Foil"


class CheapestNonFoilStrategy(SelectionStrategy):
    """
    Strategy that selects the cheapest non-foil card.
    """
    
    def select(self, offers: List[Offer]) -> Optional[Offer]:
        """
        Select the cheapest non-foil offer from the list.
        
        Args:
            offers: A list of Offer objects
        
        Returns:
            The cheapest non-foil offer, or None if no non-foil offers are available
        """
        if not offers:
            return None
        
        # Filter for available non-foil offers
        non_foil_offers = [o for o in offers if not o.foil and o.availability]
        
        if not non_foil_offers:
            return None
        
        return min(non_foil_offers, key=lambda x: x.price)
    
    def get_name(self) -> str:
        return "Cheapest Non-Foil"


class BlingiestStrategy(SelectionStrategy):
    """
    Strategy that selects the most expensive foil card (for "bling" factor).
    """
    
    def select(self, offers: List[Offer]) -> Optional[Offer]:
        """
        Select the most expensive foil offer from the list.
        
        Args:
            offers: A list of Offer objects
        
        Returns:
            The most expensive foil offer, or None if no foil offers are available
        """
        if not offers:
            return None
        
        # Filter for available foil offers
        foil_offers = [o for o in offers if o.foil and o.availability]
        
        if not foil_offers:
            return None
        
        return max(foil_offers, key=lambda x: x.price)
    
    def get_name(self) -> str:
        return "Blingiest (Most Expensive Foil)"


class BestConditionStrategy(SelectionStrategy):
    """
    Strategy that selects the cheapest offer in Near Mint condition.
    """
    
    NEAR_MINT_CONDITIONS = ["Near Mint", "NM", "Mint", "M"]
    
    def select(self, offers: List[Offer]) -> Optional[Offer]:
        """
        Select the cheapest Near Mint condition offer.
        
        Args:
            offers: A list of Offer objects
        
        Returns:
            The cheapest NM offer, or None if no NM offers are available
        """
        if not offers:
            return None
        
        # Filter for available Near Mint offers
        nm_offers = [
            o for o in offers 
            if o.availability and any(
                nm_cond.lower() in o.condition.lower() 
                for nm_cond in self.NEAR_MINT_CONDITIONS
            )
        ]
        
        if not nm_offers:
            return None
        
        return min(nm_offers, key=lambda x: x.price)
    
    def get_name(self) -> str:
        return "Best Condition (Near Mint)"


# Registry of available strategies
AVAILABLE_STRATEGIES = {
    "cheapest": CheapestStrategy(),
    "cheapest-foil": CheapestFoilStrategy(),
    "cheapest-nonfoil": CheapestNonFoilStrategy(),
    "blingiest": BlingiestStrategy(),
    "best-condition": BestConditionStrategy(),
}


def get_strategy(strategy_name: str) -> SelectionStrategy:
    """
    Get a selection strategy by name.
    
    Args:
        strategy_name: The name of the strategy (e.g., "cheapest", "cheapest-foil")
    
    Returns:
        The requested SelectionStrategy instance
    
    Raises:
        ValueError: If the strategy name is not recognized
    """
    strategy = AVAILABLE_STRATEGIES.get(strategy_name.lower())
    
    if strategy is None:
        available = ", ".join(AVAILABLE_STRATEGIES.keys())
        raise ValueError(
            f"Unknown strategy: {strategy_name}. "
            f"Available strategies: {available}"
        )
    
    return strategy
