"""
Excel output generation for MTG deal results.

This module provides functionality to export card offers and price
comparisons to Excel spreadsheets using pandas.
"""

from typing import List
from pathlib import Path
import pandas as pd
from mtg_deal_finder.cards import Offer


def create_dataframe(offers: List[Offer]) -> pd.DataFrame:
    """
    Convert a list of offers to a pandas DataFrame.
    
    Args:
        offers: A list of Offer objects
    
    Returns:
        A pandas DataFrame with columns for all offer attributes
    """
    if not offers:
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=["Card", "Set", "Condition", "Foil", "Price", "Store", "URL"])
    
    data = {
        "Card": [offer.card for offer in offers],
        "Set": [offer.set for offer in offers],
        "Condition": [offer.condition for offer in offers],
        "Foil": [offer.foil for offer in offers],
        "Price": [offer.price for offer in offers],
        "Store": [offer.store for offer in offers],
        "URL": [offer.url for offer in offers],
    }
    
    return pd.DataFrame(data)


def export_to_excel(offers: List[Offer], output_path: str) -> None:
    """
    Export offers to an Excel file.
    
    Args:
        offers: A list of Offer objects
        output_path: The path where the Excel file should be saved
    
    Raises:
        ValueError: If output_path is invalid
        IOError: If the file cannot be written
    
    Example:
        >>> offers = [Offer("Store1", "Lightning Bolt", "M11", "NM", 1.99, "url")]
        >>> export_to_excel(offers, "results.xlsx")
    """
    if not output_path:
        raise ValueError("Output path cannot be empty")
    
    # Ensure .xlsx extension
    path = Path(output_path)
    if path.suffix.lower() not in ['.xlsx', '.xls']:
        path = path.with_suffix('.xlsx')
    
    # Create DataFrame
    df = create_dataframe(offers)
    
    # Sort by price (cheapest first)
    if not df.empty:
        df = df.sort_values(by="Price", ascending=True)
    
    # Export to Excel
    try:
        df.to_excel(str(path), index=False, engine='openpyxl')
    except Exception as e:
        raise IOError(f"Failed to write Excel file: {e}")


def format_results_table(offers: List[Offer]) -> str:
    """
    Format offers as a text table for console output.
    
    Args:
        offers: A list of Offer objects
    
    Returns:
        A formatted string representation of the offers
    """
    if not offers:
        return "No offers found."
    
    df = create_dataframe(offers)
    
    # Sort by price
    df = df.sort_values(by="Price", ascending=True)
    
    return df.to_string(index=False)
