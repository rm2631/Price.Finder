"""
MTG Deal Finder - Main CLI entrypoint.

This module provides the command-line interface for the MTG Deal Finder tool.
It handles argument parsing, logging setup, and orchestrates the search and
comparison workflow.
"""

import logging
import sys
from argparse import ArgumentParser
from typing import List, Dict, Optional

from mtg_deal_finder.cards import Card, Offer
from mtg_deal_finder.stores.facetoface import FaceToFaceScraper
from mtg_deal_finder.stores.topdeckhero import TopDeckHeroScraper
from mtg_deal_finder.strategies import get_strategy, AVAILABLE_STRATEGIES
from mtg_deal_finder.output import export_to_excel, format_results_table
from mtg_deal_finder.quality import CardQuality, QUALITY_OPTIONS


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
    
    parser.add_argument(
        "--strategy",
        "-s",
        default="cheapest",
        help=f"Selection strategy for choosing the best card offer. "
             f"Options: {', '.join(AVAILABLE_STRATEGIES.keys())} (default: cheapest)"
    )
    
    parser.add_argument(
        "--min-quality",
        "-q",
        help=f"Minimum card quality/condition to consider. "
             f"Options: {', '.join(QUALITY_OPTIONS)} (default: no restriction). "
             f"This filters out cards below the specified condition. "
             f"For example, '--min-quality lp' will only show Lightly Played or better cards."
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


def search_all_stores(cards: List[Card], store_filter: str = None, use_cache: bool = True) -> Dict[str, List[Offer]]:
    """
    Search all configured stores for the given cards.
    
    Args:
        cards: A list of Card objects to search for
        store_filter: Optional comma-separated list of store names to search
        use_cache: Whether to use caching for search results (default: True)
    
    Returns:
        A dictionary mapping card names to lists of offers
    """
    logger = logging.getLogger(__name__)
    
    # Initialize available scrapers
    scrapers = {
        "facetoface": FaceToFaceScraper(use_cache=use_cache),
        "topdeckhero": TopDeckHeroScraper(use_cache=use_cache),
    }
    
    # Filter scrapers if specified
    if store_filter:
        requested_stores = [s.strip().lower() for s in store_filter.split(',')]
        scrapers = {
            name: scraper 
            for name, scraper in scrapers.items() 
            if name in requested_stores
        }
        
        if not scrapers:
            logger.error(f"No valid stores found in filter: {store_filter}")
            return {}
    
    logger.info(f"Searching {len(scrapers)} store(s): {', '.join(scrapers.keys())}")
    
    # Collect all offers for each card
    card_offers = {}
    
    for card in cards:
        logger.info(f"\nSearching for: {card.name}")
        all_offers = []
        
        for store_name, scraper in scrapers.items():
            try:
                offers = scraper.search(card)
                all_offers.extend(offers)
                logger.info(f"  {store_name}: Found {len(offers)} offer(s)")
            except Exception as e:
                logger.error(f"  {store_name}: Error searching - {e}")
        
        card_offers[card.name] = all_offers
    
    return card_offers


def select_best_offers(
    card_offers: Dict[str, List[Offer]], 
    cards: List[Card],
    strategy_name: str = "cheapest",
    min_quality: Optional[CardQuality] = None
) -> List[Offer]:
    """
    Select the best offer for each card based on the given strategy.
    
    Args:
        card_offers: A dictionary mapping card names to lists of offers
        cards: Original list of Card objects (for quantity info)
        strategy_name: Name of the selection strategy to use
        min_quality: Minimum quality level to filter offers, or None for no restriction
    
    Returns:
        A list of selected best offers
    """
    logger = logging.getLogger(__name__)
    
    try:
        strategy = get_strategy(strategy_name, min_quality)
        strategy_desc = strategy.get_name()
        if min_quality:
            strategy_desc += f" (minimum quality: {min_quality.to_display_name()})"
        logger.info(f"\nUsing selection strategy: {strategy_desc}")
    except ValueError as e:
        logger.error(str(e))
        logger.info("Falling back to 'cheapest' strategy")
        strategy = get_strategy("cheapest", min_quality)
    
    selected_offers = []
    
    for card in cards:
        offers = card_offers.get(card.name, [])
        
        if not offers:
            logger.warning(f"No offers found for: {card.name}")
            continue
        
        best_offer = strategy.select(offers)
        
        if best_offer:
            logger.info(f"Selected for {card.name}: ${best_offer.price:.2f} from {best_offer.store}")
            selected_offers.append(best_offer)
        else:
            logger.warning(f"No suitable offer found for {card.name} with strategy '{strategy_name}'")
    
    return selected_offers


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
    
    # Search all stores for cards
    logger.info("\nSearching stores...")
    card_offers = search_all_stores(cards, args.store, use_cache=not args.no_cache)
    
    # Calculate total offers found
    total_offers = sum(len(offers) for offers in card_offers.values())
    logger.info(f"\nTotal offers found: {total_offers}")
    
    if total_offers == 0:
        logger.warning("No offers found. Exiting.")
        return
    
    # Parse minimum quality if provided
    min_quality = None
    if args.min_quality:
        min_quality = CardQuality.from_string(args.min_quality)
        if min_quality is None:
            logger.error(f"Invalid minimum quality: {args.min_quality}")
            logger.info(f"Valid options: {', '.join(QUALITY_OPTIONS)}")
            return
        logger.info(f"Filtering for minimum quality: {min_quality.to_display_name()}")
    
    # Select best offers based on strategy
    selected_offers = select_best_offers(card_offers, cards, args.strategy, min_quality)
    
    if not selected_offers:
        logger.warning("No suitable offers selected. Exiting.")
        return
    
    # Display results
    logger.info("\n" + "=" * 50)
    logger.info("SELECTED BEST DEALS:")
    logger.info("=" * 50)
    logger.info("\n" + format_results_table(selected_offers))
    
    # Calculate total cost
    total_cost = sum(offer.price for offer in selected_offers)
    logger.info(f"\nTotal cost: ${total_cost:.2f}")
    
    # Export to Excel
    try:
        export_to_excel(selected_offers, args.out)
        logger.info(f"\nResults exported to: {args.out}")
    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        return
    
    logger.info("\nDone!")


if __name__ == "__main__":
    main()
