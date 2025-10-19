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
from bs4 import BeautifulSoup

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
    SEARCH_URL = f"{BASE_URL}/search"
    STORE_NAME = "FaceToFaceGames"
    
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
            
            # Construct search URL
            search_query = quote_plus(card.name)
            search_url = f"{self.SEARCH_URL}?q={search_query}"
            
            # Make the request
            logger.debug(f"Fetching: {search_url}")
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract offers from the page
            offers = self._parse_offers(soup, card.name, search_url)
            
            logger.info(f"Found {len(offers)} offer(s) for {card.name}")
            return offers
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from FaceToFaceGames: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error while searching FaceToFaceGames: {e}")
            return []
    
    def _parse_offers(self, soup: BeautifulSoup, card_name: str, search_url: str) -> List[Offer]:
        """
        Parse offers from the search results page.
        
        Args:
            soup: BeautifulSoup object of the search results page
            card_name: The name of the card being searched
            search_url: The URL that was searched
        
        Returns:
            A list of Offer objects
        """
        offers = []
        
        # FaceToFaceGames typically uses product cards or list items for search results
        # Common selectors might be: .product-item, .product-card, .search-result, etc.
        # We'll try multiple common patterns
        
        product_elements = (
            soup.find_all('div', class_=re.compile(r'product[-_]?(item|card|result)', re.I)) or
            soup.find_all('li', class_=re.compile(r'product[-_]?(item|card|result)', re.I)) or
            soup.find_all('article', class_=re.compile(r'product', re.I)) or
            soup.find_all('div', class_=re.compile(r'item', re.I))
        )
        
        logger.debug(f"Found {len(product_elements)} potential product elements")
        
        for element in product_elements:
            try:
                offer = self._parse_single_offer(element, card_name, search_url)
                if offer:
                    offers.append(offer)
            except Exception as e:
                logger.debug(f"Error parsing product element: {e}")
                continue
        
        return offers
    
    def _parse_single_offer(self, element, card_name: str, fallback_url: str) -> Offer:
        """
        Parse a single offer from a product element.
        
        Args:
            element: BeautifulSoup element representing a single product
            card_name: The name of the card being searched
            fallback_url: URL to use if no specific product URL is found
        
        Returns:
            An Offer object, or None if parsing fails or the card is non-English
        """
        # Extract card title
        title_elem = (
            element.find('h2', class_=re.compile(r'title|name|product', re.I)) or
            element.find('h3', class_=re.compile(r'title|name|product', re.I)) or
            element.find('a', class_=re.compile(r'title|name|product', re.I)) or
            element.find(class_=re.compile(r'product[-_]?name|product[-_]?title', re.I))
        )
        
        if not title_elem:
            return None
        
        full_title = title_elem.get_text(strip=True)
        
        # Filter out non-English cards
        if self._is_non_english(full_title):
            logger.debug(f"Skipping non-English card: {full_title}")
            return None
        
        # Extract set information
        card_set = self._extract_set(element, full_title)
        
        # Extract condition
        condition = self._extract_condition(element)
        
        # Extract price
        price = self._extract_price(element)
        if price is None:
            return None
        
        # Extract foil status
        is_foil = self._is_foil(element, full_title)
        
        # Extract availability
        in_stock = self._extract_availability(element)
        
        # Extract URL
        url = self._extract_url(element, fallback_url)
        
        # Clean up card name (remove set info, foil markers, etc.)
        clean_card_name = self._clean_card_name(full_title)
        
        return Offer(
            store=self.STORE_NAME,
            card=clean_card_name,
            set=card_set,
            condition=condition,
            price=price,
            url=url,
            foil=is_foil,
            availability=in_stock
        )
    
    def _is_non_english(self, title: str) -> bool:
        """
        Check if a card title indicates a non-English version.
        
        Args:
            title: The card title to check
        
        Returns:
            True if the card is non-English, False otherwise
        """
        # Look for language markers in parentheses
        language_markers = [
            'french', 'japanese', 'german', 'spanish', 'italian',
            'portuguese', 'russian', 'korean', 'chinese', 'simplified chinese',
            'traditional chinese'
        ]
        
        title_lower = title.lower()
        for marker in language_markers:
            if f'({marker})' in title_lower or f'[{marker}]' in title_lower:
                return True
        
        return False
    
    def _extract_set(self, element, title: str) -> str:
        """
        Extract set information from the product element or title.
        
        Args:
            element: BeautifulSoup element
            title: The card title
        
        Returns:
            The set name or "Unknown"
        """
        # Try to find set in a dedicated element
        set_elem = (
            element.find(class_=re.compile(r'set|edition', re.I)) or
            element.find('span', class_=re.compile(r'variant|version', re.I))
        )
        
        if set_elem:
            return set_elem.get_text(strip=True)
        
        # Try to extract from title (often in brackets or parentheses)
        # Pattern: "Card Name [SET]" or "Card Name (SET)"
        set_match = re.search(r'\[([^\]]+)\]|\(([^)]+)\)', title)
        if set_match:
            return set_match.group(1) or set_match.group(2)
        
        return "Unknown"
    
    def _extract_condition(self, element) -> str:
        """
        Extract condition information from the product element.
        
        Args:
            element: BeautifulSoup element
        
        Returns:
            The condition string (e.g., "Near Mint", "Lightly Played")
        """
        condition_elem = element.find(class_=re.compile(r'condition|grade', re.I))
        
        if condition_elem:
            return condition_elem.get_text(strip=True)
        
        # Check for common condition abbreviations
        text = element.get_text()
        condition_patterns = [
            (r'\bNM\b', 'Near Mint'),
            (r'\bLP\b', 'Lightly Played'),
            (r'\bMP\b', 'Moderately Played'),
            (r'\bHP\b', 'Heavily Played'),
            (r'\bDMG\b', 'Damaged'),
            (r'Near Mint', 'Near Mint'),
            (r'Lightly Played', 'Lightly Played'),
            (r'Moderately Played', 'Moderately Played'),
            (r'Heavily Played', 'Heavily Played'),
            (r'Damaged', 'Damaged'),
        ]
        
        for pattern, condition in condition_patterns:
            if re.search(pattern, text, re.I):
                return condition
        
        return "Near Mint"  # Default assumption
    
    def _extract_price(self, element) -> float:
        """
        Extract price from the product element.
        
        Args:
            element: BeautifulSoup element
        
        Returns:
            The price as a float, or None if not found
        """
        # Look for price element
        price_elem = (
            element.find(class_=re.compile(r'price', re.I)) or
            element.find('span', class_=re.compile(r'amount|cost', re.I))
        )
        
        if not price_elem:
            return None
        
        price_text = price_elem.get_text(strip=True)
        
        # Extract numeric value (handle various formats: $1.99, 1.99, $1,999.99, etc.)
        price_match = re.search(r'[\$]?\s*([\d,]+\.?\d*)', price_text)
        if price_match:
            try:
                price_str = price_match.group(1).replace(',', '')
                return float(price_str)
            except ValueError:
                return None
        
        return None
    
    def _is_foil(self, element, title: str) -> bool:
        """
        Determine if the card is foil.
        
        Args:
            element: BeautifulSoup element
            title: The card title
        
        Returns:
            True if the card is foil, False otherwise
        """
        # Check title for foil indicator
        title_lower = title.lower()
        if 'foil' in title_lower:
            return True
        
        # Check for foil class or attribute
        if element.find(class_=re.compile(r'foil', re.I)):
            return True
        
        # Check element text
        if 'foil' in element.get_text().lower():
            return True
        
        return False
    
    def _extract_availability(self, element) -> bool:
        """
        Extract availability status from the product element.
        
        Args:
            element: BeautifulSoup element
        
        Returns:
            True if in stock, False otherwise
        """
        # Look for availability indicators
        stock_elem = element.find(class_=re.compile(r'stock|availability|inventory', re.I))
        
        if stock_elem:
            stock_text = stock_elem.get_text(strip=True).lower()
            # Check for out of stock indicators
            if any(phrase in stock_text for phrase in ['out of stock', 'sold out', 'unavailable']):
                return False
            # Check for in stock indicators
            if any(phrase in stock_text for phrase in ['in stock', 'available', 'in-stock']):
                return True
        
        # Check for buttons (add to cart usually means in stock)
        add_button = element.find('button', class_=re.compile(r'add[-_]?to[-_]?cart', re.I))
        if add_button:
            # Check if button is disabled
            if add_button.get('disabled'):
                return False
            return True
        
        # Default to true (assume available unless proven otherwise)
        return True
    
    def _extract_url(self, element, fallback_url: str) -> str:
        """
        Extract product URL from the element.
        
        Args:
            element: BeautifulSoup element
            fallback_url: URL to use if no specific URL is found
        
        Returns:
            The product URL
        """
        # Look for link in title or product element
        link_elem = (
            element.find('a', href=True) or
            element.find('a', class_=re.compile(r'product|title|link', re.I))
        )
        
        if link_elem and link_elem.get('href'):
            href = link_elem['href']
            # Make absolute URL if needed
            if href.startswith('/'):
                return f"{self.BASE_URL}{href}"
            elif href.startswith('http'):
                return href
            else:
                return f"{self.BASE_URL}/{href}"
        
        return fallback_url
    
    def _clean_card_name(self, title: str) -> str:
        """
        Clean up the card name by removing set info, foil markers, etc.
        
        Args:
            title: The full card title
        
        Returns:
            The cleaned card name
        """
        # Remove set information in brackets or parentheses
        cleaned = re.sub(r'\[([^\]]+)\]|\(([^)]+)\)', '', title)
        
        # Remove foil indicator
        cleaned = re.sub(r'\bfoil\b', '', cleaned, flags=re.I)
        
        # Remove extra whitespace and dashes
        cleaned = ' '.join(cleaned.split())
        cleaned = re.sub(r'\s*-\s*$', '', cleaned)  # Remove trailing dash
        cleaned = re.sub(r'^\s*-\s*', '', cleaned)  # Remove leading dash
        
        return cleaned.strip()
