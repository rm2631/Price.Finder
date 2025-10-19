"""
Store scrapers package.

This package contains the base scraper interface and implementations
for various MTG card stores.
"""

from mtg_deal_finder.stores.base import StoreScraper
from mtg_deal_finder.stores.facetoface import FaceToFaceScraper

__all__ = ['StoreScraper', 'FaceToFaceScraper']
