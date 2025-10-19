"""
FaceToFaceGames store scraper implementation.

This module implements the StoreScraper interface for FaceToFaceGames,
a Canadian Magic: The Gathering card store.
"""

import logging
import re
from typing import List
from urllib.parse import quote_plus

import requests

from mtg_deal_finder.cards import Card, Offer
from mtg_deal_finder.stores.base import StoreScraper


logger = logging.getLogger(__name__)


class FaceToFaceScraper(StoreScraper):
    """
    Scraper for FaceToFaceGames store.
    
    This scraper searches for Magic: The Gathering cards on FaceToFaceGames
    and returns available offers including price, set, condition, and availability.
    """
    
    BASE_URL = "https://facetofacegames.com"
    API_URL = f"{BASE_URL}/apps/prod-indexer/search"
    STORE_NAME = "FaceToFaceGames"
    
    # Condition mapping from SKU codes to readable names
    CONDITION_MAP = {
        'NM': 'Near Mint',
        'LP': 'Lightly Played',
        'MP': 'Moderately Played',
        'PL': 'Played',
        'HP': 'Heavily Played',
        'DMG': 'Damaged',
    }
    
    def __init__(self):
        """Initialize the scraper with a requests session."""
        self.session = requests.Session()
        # Set a user agent to appear as a regular browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search(self, card: Card) -> List[Offer]:
        """
        Search for a card on FaceToFaceGames and return available offers.
        
        Args:
            card: A Card object containing the card name and optional set/quantity
        
        Returns:
            A list of Offer objects representing available offers for the card.
            Returns an empty list if no offers are found or if an error occurs.
        """
        try:
            logger.info(f"Searching FaceToFaceGames for: {card.name}")
            
            # Construct API URL
            # Note: The FaceToFaceGames API expects double URL encoding for the search query.
            # This is because the API internally decodes the query twice - once at the web server level
            # and once at the application level. Single encoding would result in incorrect search queries.
            search_query = quote_plus(quote_plus(card.name))
            api_url = f"{self.API_URL}/keyword/{search_query}/pageSize/50/page/1"
            
            # Make the request
            logger.debug(f"Fetching API: {api_url}")
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Extract offers from the hits
            offers = self._parse_api_response(data, card.name)
            
            logger.info(f"Found {len(offers)} offer(s) for {card.name}")
            return offers
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from FaceToFaceGames: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error while searching FaceToFaceGames: {e}")
            return []
    
    def _parse_api_response(self, data: dict, card_name: str) -> List[Offer]:
        """
        Parse offers from the API JSON response.
        
        Args:
            data: The JSON response data from the API
            card_name: The name of the card being searched
        
        Returns:
            A list of Offer objects
        """
        offers = []
        
        try:
            hits = data.get('hits', {}).get('hits', [])
            logger.debug(f"Processing {len(hits)} product hits")
            
            for hit in hits:
                source = hit.get('_source', {})
                
                # Filter out non-English cards
                if self._is_non_english(source.get('title', '')):
                    logger.debug(f"Skipping non-English card: {source.get('title', '')}")
                    continue
                
                # Process each variant (different conditions)
                variants = source.get('variants', [])
                for variant in variants:
                    try:
                        offer = self._parse_variant(source, variant, card_name)
                        if offer:
                            offers.append(offer)
                    except Exception as e:
                        logger.debug(f"Error parsing variant: {e}")
                        continue
            
        except Exception as e:
            logger.error(f"Error parsing API response: {e}")
        
        return offers
    
    def _parse_variant(self, product: dict, variant: dict, card_name: str) -> Offer:
        """
        Parse a single variant (condition) into an Offer.
        
        Args:
            product: The product data from the API
            variant: The variant data (represents one condition option)
            card_name: The original card name searched
        
        Returns:
            An Offer object, or None if the variant is not valid
        """
        # Extract basic info
        title = product.get('title', '')
        handle = product.get('handle', '')
        
        # Extract price
        price = variant.get('price')
        if price is None:
            return None
        
        # Extract inventory and availability
        inventory = variant.get('inventoryQuantity', 0)
        is_available = inventory > 0
        
        # Extract condition from selectedOptions
        condition = 'Unknown'
        selected_options = variant.get('selectedOptions', [])
        for option in selected_options:
            if option.get('name') == 'Condition':
                condition_code = option.get('value', 'Unknown')
                condition = self.CONDITION_MAP.get(condition_code, condition_code)
                break
        
        # Determine if foil
        is_foil = self._is_foil(title)
        
        # Extract set information
        card_set = self._extract_set(title)
        
        # Clean up card name
        clean_name = self._clean_card_name(title)
        
        # Construct product URL
        url = f"{self.BASE_URL}/products/{handle}"
        
        return Offer(
            store=self.STORE_NAME,
            card=clean_name,
            set=card_set,
            condition=condition,
            price=price,
            url=url,
            foil=is_foil,
            availability=is_available
        )
    
    def _is_non_english(self, title: str) -> bool:
        """
        Check if a card title indicates a non-English version.
        
        Args:
            title: The card title to check
        
        Returns:
            True if the card is non-English, False otherwise
        """
        # Look for language markers in the title
        # FaceToFaceGames formats non-English cards as: "Card Name - Language [Set]"
        # Example: "Lightning Bolt - Japanese [123] [Set Name] [Foil]"
        language_markers = [
            ' - french', ' - japanese', ' - german', ' - spanish', ' - italian',
            ' - portuguese', ' - russian', ' - korean', ' - chinese', 
            ' - simplified chinese', ' - traditional chinese'
        ]
        
        title_lower = title.lower()
        for marker in language_markers:
            if marker in title_lower:
                return True
        
        return False
    
    def _extract_set(self, title: str) -> str:
        """
        Extract set information from the product title.
        
        Args:
            title: The card title
        
        Returns:
            The set name or "Unknown"
        """
        # FaceToFaceGames format: "Card Name [Number] [Set Name] [Foil/Non-Foil]"
        # Example: "Lightning Bolt [117] [Double Masters 2022] [Foil]"
        
        # Extract all text within brackets
        all_brackets = re.findall(r'\[([^\]]+)\]', title)
        
        if len(all_brackets) >= 2:
            # Second bracket is usually the set name
            # First bracket is typically the card number
            return all_brackets[1]
        elif len(all_brackets) == 1:
            # If only one bracket, check if it looks like a set name
            # Set names are typically not purely numeric and not foil/non-foil indicators
            bracket_content = all_brackets[0]
            if bracket_content.lower() not in ['foil', 'non-foil'] and not bracket_content.isdigit():
                return bracket_content
        
        return "Unknown"
    
    def _is_foil(self, title: str) -> bool:
        """
        Determine if the card is foil.
        
        Args:
            title: The card title
        
        Returns:
            True if the card is foil, False otherwise
        """
        title_lower = title.lower()
        
        # Check for [Non-Foil] first - if present, definitely not foil
        if '[non-foil]' in title_lower or '(non-foil)' in title_lower:
            return False
        
        # Check for [Foil] indicator
        return '[foil]' in title_lower or '(foil)' in title_lower
    
    def _clean_card_name(self, title: str) -> str:
        """
        Clean up the card name by removing set info, foil markers, etc.
        
        Args:
            title: The full card title
        
        Returns:
            The cleaned card name
        """
        # Remove everything in brackets
        cleaned = re.sub(r'\[([^\]]+)\]', '', title)
        
        # Remove foil indicator
        cleaned = re.sub(r'\bfoil\b', '', cleaned, flags=re.I)
        
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        cleaned = cleaned.strip()
        
        return cleaned
