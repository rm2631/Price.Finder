"""
TopDeckHero store scraper implementation.

This module implements the StoreScraper interface for TopDeckHero,
a Canadian Magic: The Gathering card store.
"""

import logging
import re
import time
from typing import List
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from mtg_deal_finder.cards import Card, Offer
from mtg_deal_finder.stores.base import StoreScraper
from mtg_deal_finder.utils.caching import load_from_cache, save_to_cache


logger = logging.getLogger(__name__)


class TopDeckHeroScraper(StoreScraper):
    """
    Scraper for TopDeckHero store.
    
    This scraper searches for Magic: The Gathering cards on TopDeckHero
    and returns available offers including price, set, condition, and availability.
    """
    
    BASE_URL = "https://www.topdeckhero.com"
    SEARCH_URL = f"{BASE_URL}/products/search"
    STORE_NAME = "TopDeckHero"
    
    # Condition mapping from display text to normalized names
    CONDITION_MAP = {
        'Near Mint': 'Near Mint',
        'Lightly Played': 'Lightly Played',
        'Moderately Played': 'Moderately Played',
        'Played': 'Played',
        'Heavy Played': 'Heavily Played',
        'Heavily Played': 'Heavily Played',
        'Damaged': 'Damaged',
    }
    
    def __init__(self, use_cache: bool = True, apply_discount: bool = False):
        """
        Initialize the scraper with a requests session.
        
        Args:
            use_cache: Whether to use caching for search results (default: True)
            apply_discount: Whether to apply the 20% checkout discount (default: False)
        """
        self.session = requests.Session()
        # Set a user agent to appear as a regular browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.use_cache = use_cache
        self.apply_discount = apply_discount
        self.discount_rate = 0.20  # 20% discount
    
    def search(self, card: Card, max_pages: int = 2) -> List[Offer]:
        """
        Search for a card on TopDeckHero and return available offers.
        
        Args:
            card: A Card object containing the card name and optional set/quantity
            max_pages: Maximum number of pages to scrape (default: 2)
        
        Returns:
            A list of Offer objects representing available offers for the card.
            Returns an empty list if no offers are found or if an error occurs.
        """
        try:
            logger.info(f"Searching TopDeckHero for: {card.name}")
            
            # Check cache first
            if self.use_cache:
                cached_data = load_from_cache(self.STORE_NAME, card.name)
                if cached_data:
                    logger.info(f"Using cached data for {card.name}")
                    # Convert cached data back to Offer objects
                    return self._deserialize_offers(cached_data)
            
            # Collect offers from multiple pages
            all_offers = []
            
            for page_num in range(1, max_pages + 1):
                logger.debug(f"Fetching page {page_num} for {card.name}")
                
                # Construct search URL with pagination
                params = {
                    'q': card.name,
                }
                if page_num > 1:
                    params['page'] = page_num
                
                # Make the request
                response = self.session.get(self.SEARCH_URL, params=params, timeout=10)
                response.raise_for_status()
                
                # Parse HTML response
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract offers from the page
                page_offers = self._parse_search_results(soup, card.name)
                
                if not page_offers:
                    logger.debug(f"No more results on page {page_num}, stopping pagination")
                    break
                
                all_offers.extend(page_offers)
                
                # Add a small delay between pages to be polite
                if page_num < max_pages:
                    time.sleep(0.5)
            
            logger.info(f"Found {len(all_offers)} offer(s) for {card.name}")
            
            # Save to cache
            if self.use_cache and all_offers:
                save_to_cache(self.STORE_NAME, card.name, self._serialize_offers(all_offers))
            
            return all_offers
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from TopDeckHero: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error while searching TopDeckHero: {e}")
            return []
    
    def _parse_search_results(self, soup: BeautifulSoup, card_name: str) -> List[Offer]:
        """
        Parse offers from the search results page.
        
        Args:
            soup: BeautifulSoup object of the search results page
            card_name: The name of the card being searched
        
        Returns:
            A list of Offer objects
        """
        offers = []
        
        try:
            # Find all product listings
            products = soup.find_all('li', class_='product')
            logger.debug(f"Found {len(products)} product listings on page")
            
            for product in products:
                try:
                    # Extract basic product info
                    name_elem = product.find('h4', class_='name')
                    if not name_elem:
                        continue
                    
                    product_name = name_elem.get_text(strip=True)
                    
                    # Extract set/category
                    category_elem = product.find('span', class_='category')
                    product_set = category_elem.get_text(strip=True) if category_elem else "Unknown"
                    
                    # Extract product URL
                    url_elem = product.find('a', itemprop='url')
                    product_url = self.BASE_URL + url_elem.get('href') if url_elem else ""
                    
                    # Find all variants (different conditions) for this product
                    variants = product.find_all('div', class_='variant-row')
                    
                    for variant in variants:
                        try:
                            offer = self._parse_variant(variant, product_name, product_set, product_url)
                            if offer:
                                offers.append(offer)
                        except Exception as e:
                            logger.debug(f"Error parsing variant: {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Error parsing product: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing search results: {e}")
        
        return offers
    
    def _parse_variant(self, variant: BeautifulSoup, product_name: str, 
                      product_set: str, product_url: str) -> Offer:
        """
        Parse a single variant (condition) into an Offer.
        
        Args:
            variant: BeautifulSoup object of the variant row
            product_name: The product name
            product_set: The product set/category
            product_url: The product URL
        
        Returns:
            An Offer object, or None if the variant is not valid
        """
        # Check if variant is in stock
        is_available = 'in-stock' in variant.get('class', [])
        
        # Extract variant description (condition, language)
        desc_elem = variant.find('span', class_='variant-description')
        if not desc_elem:
            return None
        
        variant_desc = desc_elem.get_text(strip=True)
        
        # Parse condition and language from description
        # Format is typically: "Condition, Language" (e.g., "Near Mint, English")
        parts = [p.strip() for p in variant_desc.split(',')]
        
        condition = 'Unknown'
        language = 'English'  # Default to English if not specified
        
        if len(parts) >= 2:
            condition_raw = parts[0]
            language = parts[1]
            # Normalize condition
            condition = self.CONDITION_MAP.get(condition_raw, condition_raw)
        elif len(parts) == 1:
            # Only condition provided, assume English
            condition_raw = parts[0]
            condition = self.CONDITION_MAP.get(condition_raw, condition_raw)
        
        # Filter out non-English cards
        if language.lower() != 'english':
            logger.debug(f"Skipping non-English card: {product_name} ({language})")
            return None
        
        # Extract price from form data-price attribute
        form = variant.find('form', class_='add-to-cart-form')
        if not form:
            return None
        
        price_str = form.get('data-price', '')
        if not price_str:
            return None
        
        # Parse price - format is typically "CAD$ X.XX"
        price_match = re.search(r'[\d.]+', price_str)
        if not price_match:
            return None
        
        try:
            price = float(price_match.group())
        except (ValueError, AttributeError):
            return None
        
        # Apply discount if enabled
        if self.apply_discount:
            price = price * (1 - self.discount_rate)
        
        # Determine if foil
        # TopDeckHero uses a foil icon with class 'ss-foil'
        is_foil = variant.find('i', class_='ss-foil') is not None
        
        # Clean up card name
        clean_name = self._clean_card_name(product_name)
        
        return Offer(
            store=self.STORE_NAME,
            card=clean_name,
            set=product_set,
            condition=condition,
            price=price,
            url=product_url,
            foil=is_foil,
            availability=is_available
        )
    
    def _clean_card_name(self, title: str) -> str:
        """
        Clean up the card name by removing extra markers.
        
        Args:
            title: The full card title
        
        Returns:
            The cleaned card name
        """
        # Remove extra whitespace
        cleaned = ' '.join(title.split())
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _serialize_offers(self, offers: List[Offer]) -> List[dict]:
        """
        Serialize offers to dictionaries for caching.
        
        Args:
            offers: List of Offer objects
        
        Returns:
            List of dictionaries
        """
        return [
            {
                'store': offer.store,
                'card': offer.card,
                'set': offer.set,
                'condition': offer.condition,
                'price': offer.price,
                'url': offer.url,
                'foil': offer.foil,
                'availability': offer.availability
            }
            for offer in offers
        ]
    
    def _deserialize_offers(self, data: List[dict]) -> List[Offer]:
        """
        Deserialize cached data back to Offer objects.
        
        Args:
            data: List of dictionaries
        
        Returns:
            List of Offer objects
        """
        return [
            Offer(
                store=item['store'],
                card=item['card'],
                set=item['set'],
                condition=item['condition'],
                price=item['price'],
                url=item['url'],
                foil=item['foil'],
                availability=item['availability']
            )
            for item in data
        ]
