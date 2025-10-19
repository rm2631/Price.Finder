"""
Proxy card "scraper" that generates proxy offers at a fixed price.

This module provides a special scraper that generates proxy card offers
at a fixed price of $0.45 per card. Proxies are not official Magic cards
but can be used in casual play.
"""

from typing import List
from mtg_deal_finder.cards import Card, Offer
from mtg_deal_finder.stores.base import StoreScraper


class ProxyScraper(StoreScraper):
    """
    A scraper that generates proxy card offers at a fixed price.
    
    Proxies are priced at $0.45 per card and can be configured to:
    - Generate offers for all cards
    - Generate offers only for non-foil cards
    """
    
    PROXY_PRICE = 0.45
    
    def __init__(self, allow_foil: bool = False):
        """
        Initialize the proxy scraper.
        
        Args:
            allow_foil: If False (default), only non-foil proxies are generated.
                       If True, foil proxies are also generated.
        """
        self.allow_foil = allow_foil
    
    def search(self, card: Card) -> List[Offer]:
        """
        Generate proxy offers for the given card.
        
        Args:
            card: A Card object containing the card name
        
        Returns:
            A list containing one or two Offer objects (non-foil and optionally foil)
        """
        offers = []
        
        # Always generate a non-foil proxy offer
        non_foil_offer = Offer(
            store="Proxy",
            card=card.name,
            set=card.set if card.set else "Proxy",
            condition="Proxy",
            price=self.PROXY_PRICE,
            url="",
            foil=False,
            availability=True,
            query=card.name
        )
        offers.append(non_foil_offer)
        
        # Optionally generate a foil proxy offer
        if self.allow_foil:
            foil_offer = Offer(
                store="Proxy",
                card=card.name,
                set=card.set if card.set else "Proxy",
                condition="Proxy",
                price=self.PROXY_PRICE,
                url="",
                foil=True,
                availability=True,
                query=card.name
            )
            offers.append(foil_offer)
        
        return offers
