"""
Price comparison logic for MTG card offers.

This module provides functionality to aggregate and compare offers from
multiple stores, identifying the best deals for each card.
"""

from typing import List, Dict
from collections import defaultdict
from mtg_deal_finder.cards import Card, Offer


def aggregate_offers(offers: List[Offer]) -> List[Offer]:
    """
    Aggregate offers from multiple stores and sort by price.
    
    Args:
        offers: A list of Offer objects from various stores
    
    Returns:
        A sorted list of offers, with cheapest first
    """
    return sorted(offers, key=lambda x: x.price)


def find_best_deals(offers: List[Offer]) -> Dict[str, Offer]:
    """
    Find the best deal (lowest price) for each unique card.
    
    Args:
        offers: A list of Offer objects from various stores
    
    Returns:
        A dictionary mapping card names to their best offer
    
    Example:
        >>> offers = [
        ...     Offer("Store1", "Lightning Bolt", "M11", "NM", 1.99, "url1"),
        ...     Offer("Store2", "Lightning Bolt", "M11", "NM", 1.49, "url2"),
        ... ]
        >>> best = find_best_deals(offers)
        >>> best["Lightning Bolt"].price
        1.49
    """
    best_deals = {}
    
    for offer in offers:
        card_key = offer.card
        
        if card_key not in best_deals or offer.price < best_deals[card_key].price:
            best_deals[card_key] = offer
    
    return best_deals


def group_by_store(offers: List[Offer]) -> Dict[str, List[Offer]]:
    """
    Group offers by store name.
    
    Args:
        offers: A list of Offer objects from various stores
    
    Returns:
        A dictionary mapping store names to lists of their offers
    """
    grouped = defaultdict(list)
    
    for offer in offers:
        grouped[offer.store].append(offer)
    
    return dict(grouped)


def calculate_total_cost(offers: List[Offer]) -> float:
    """
    Calculate the total cost of a list of offers.
    
    Args:
        offers: A list of Offer objects
    
    Returns:
        The total price as a float
    """
    return sum(offer.price for offer in offers)
