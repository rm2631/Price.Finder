"""
MTG Deal Finder - Main CLI entrypoint.

This module provides the command-line interface for the MTG Deal Finder tool.
It handles argument parsing, logging setup, and orchestrates the search and
comparison workflow.
"""

import logging
import sys
from argparse import ArgumentParser
from typing import List

from mtg_deal_finder.cards import Card


# Configure logging
def setup_logging(debug: bool = False) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        debug: If True, set log level to DEBUG; otherwise INFO
    """
    level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def parse_arguments() -> ArgumentParser:
    """
    Parse command-line arguments.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = ArgumentParser(
        description="MTG Deal Finder - Find the best prices for Magic: The Gathering cards"
    )
    
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Path to text file with card list (one card per line)"
    )
    
    parser.add_argument(
        "--out",
        "-o",
        default="results.xlsx",
        help="Output Excel file path (default: results.xlsx)"
    )
    
    parser.add_argument(
        "--store",
        help="Comma-separated list of stores to search (e.g., facetoface,topdeckhero)"
    )
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching of search results"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    return parser


def parse_card_line(line: str) -> Card:
    """
    Parse a single line from the input file into a Card object.
    
    Supports formats:
    - "Card Name"
    - "Card Name (SET)"
    - "Card Name x4"
    - "Card Name (SET) x4"
    
    Args:
        line: A line of text representing a card
    
    Returns:
        A Card object
    """
    line = line.strip()
    if not line:
        return None
    
    # Default values
    name = line
    set_code = None
    qty = 1
    
    # Extract quantity (e.g., "x4" or "4x")
    if " x" in line.lower():
        parts = line.lower().split(" x")
        name = parts[0].strip()
        try:
            qty = int(parts[1].strip())
        except (ValueError, IndexError):
            qty = 1
    elif line.lower().endswith("x"):
        # Handle "4x Card Name" format
        parts = line.split(None, 1)
        if len(parts) == 2 and parts[0][:-1].isdigit():
            qty = int(parts[0][:-1])
            name = parts[1].strip()
    
    # Extract set code (e.g., "(7ED)")
    if "(" in name and ")" in name:
        start = name.index("(")
        end = name.index(")")
        set_code = name[start+1:end].strip()
        name = name[:start].strip()
    
    return Card(name=name, set=set_code, qty=qty)


def read_cards_from_file(filepath: str) -> List[Card]:
    """
    Read cards from a text file.
    
    Args:
        filepath: Path to the input file
    
    Returns:
        A list of Card objects
    """
    cards = []
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                card = parse_card_line(line)
                if card:
                    cards.append(card)
    except FileNotFoundError:
        logging.error(f"Input file not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading input file: {e}")
        sys.exit(1)
    
    return cards


def main() -> None:
    """
    Main application entry point.
    """
    parser = parse_arguments()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(debug=args.debug)
    logger = logging.getLogger(__name__)
    
    logger.info("MTG Deal Finder v0.1.0")
    logger.info("=" * 50)
    
    # If no input file provided, show welcome message
    if not args.input_file:
        logger.info("Welcome to MTG Deal Finder!")
        logger.info("")
        logger.info("This tool helps you find the best prices for MTG cards")
        logger.info("across multiple Canadian online stores.")
        logger.info("")
        logger.info("Usage: python -m mtg_deal_finder <input_file> [options]")
        logger.info("")
        logger.info("Example input file (one card per line):")
        logger.info("  Lightning Bolt")
        logger.info("  Sol Ring")
        logger.info("  Counterspell (7ED)")
        logger.info("  Brainstorm x4")
        logger.info("")
        logger.info("For more information, use: --help")
        return
    
    # Read cards from input file
    logger.info(f"Reading cards from: {args.input_file}")
    cards = read_cards_from_file(args.input_file)
    logger.info(f"Found {len(cards)} card(s) to search")
    
    # Display parsed cards
    for card in cards:
        set_info = f" ({card.set})" if card.set else ""
        qty_info = f" x{card.qty}" if card.qty > 1 else ""
        logger.debug(f"  - {card.name}{set_info}{qty_info}")
    
    # TODO: Implement store scraping logic
    logger.info("Store scraping not yet implemented")
    logger.info("This is a foundation setup - scrapers will be added in future updates")
    
    # For now, just show that the structure is working
    logger.info("")
    logger.info("Foundation setup complete!")
    logger.info("Next steps:")
    logger.info("  1. Implement store-specific scrapers")
    logger.info("  2. Add price comparison logic")
    logger.info("  3. Export results to Excel")


if __name__ == "__main__":
    main()
