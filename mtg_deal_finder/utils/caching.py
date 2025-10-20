"""
Caching utilities for store search results.

This module provides functionality to cache search results to avoid
redundant API calls and web scraping operations, improving performance
and reducing load on store servers.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any


# Default cache directory
CACHE_DIR = Path.home() / ".mtg_deal_finder" / "cache"


def get_cache_path(store_name: str, card_name: str) -> Path:
    """
    Get the cache file path for a specific store and card combination.
    
    Args:
        store_name: The name of the store
        card_name: The name of the card
    
    Returns:
        A Path object representing the cache file location
    """
    # Create cache directory if it doesn't exist
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create a safe filename
    safe_filename = f"{store_name}_{card_name}".replace(" ", "_").replace("/", "_")
    safe_filename = "".join(c for c in safe_filename if c.isalnum() or c in ("_", "-"))
    
    return CACHE_DIR / f"{safe_filename}.json"


def save_to_cache(store_name: str, card_name: str, data: Any, ttl_hours: int = 24) -> None:
    """
    Save search results to cache.
    
    Args:
        store_name: The name of the store
        card_name: The name of the card
        data: The data to cache (must be JSON-serializable)
        ttl_hours: Time-to-live in hours (default: 24)
    """
    cache_path = get_cache_path(store_name, card_name)
    
    cache_entry = {
        "timestamp": datetime.now().isoformat(),
        "ttl_hours": ttl_hours,
        "data": data
    }
    
    try:
        with open(cache_path, 'w') as f:
            json.dump(cache_entry, f, indent=2)
    except Exception as e:
        # Log error but don't fail the operation
        print(f"Warning: Failed to save cache: {e}")


def load_from_cache(store_name: str, card_name: str) -> Optional[Any]:
    """
    Load search results from cache if available and not expired.
    
    If the cache exists but is expired (older than the TTL), the expired
    cache file is automatically deleted to prevent stale data accumulation.
    
    Args:
        store_name: The name of the store
        card_name: The name of the card
    
    Returns:
        The cached data if available and valid, None otherwise
    """
    cache_path = get_cache_path(store_name, card_name)
    
    if not cache_path.exists():
        return None
    
    try:
        with open(cache_path, 'r') as f:
            cache_entry = json.load(f)
        
        # Check if cache is expired
        timestamp = datetime.fromisoformat(cache_entry["timestamp"])
        ttl = timedelta(hours=cache_entry.get("ttl_hours", 24))
        
        if datetime.now() - timestamp > ttl:
            # Cache expired - delete the file
            try:
                cache_path.unlink()
            except Exception as delete_error:
                print(f"Warning: Failed to delete expired cache {cache_path}: {delete_error}")
            return None
        
        return cache_entry["data"]
    
    except Exception as e:
        # Log error but don't fail the operation
        print(f"Warning: Failed to load cache: {e}")
        return None


def clear_cache(store_name: Optional[str] = None) -> int:
    """
    Clear cached data.
    
    Args:
        store_name: If provided, only clear cache for this store.
                   If None, clear all cache.
    
    Returns:
        Number of cache files deleted
    """
    if not CACHE_DIR.exists():
        return 0
    
    count = 0
    for cache_file in CACHE_DIR.glob("*.json"):
        if store_name is None or cache_file.name.startswith(f"{store_name}_"):
            try:
                cache_file.unlink()
                count += 1
            except Exception as e:
                print(f"Warning: Failed to delete cache file {cache_file}: {e}")
    
    return count
