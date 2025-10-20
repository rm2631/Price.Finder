"""
Streamlit UI for MTG Deal Finder.

This module provides a web-based user interface for the MTG Deal Finder tool,
allowing users to paste card lists and search for the best prices across stores
without using the command line.
"""

import logging
import sys
import io
from typing import List, Dict, Optional

import streamlit as st
import pandas as pd

from mtg_deal_finder.cards import Card, Offer
from mtg_deal_finder.main import (
    parse_card_line,
    search_all_stores,
    select_best_offers,
    setup_logging
)
from mtg_deal_finder.strategies import AVAILABLE_STRATEGIES
from mtg_deal_finder.quality import CardQuality, QUALITY_OPTIONS
from mtg_deal_finder.output import create_dataframe


# Configure page
st.set_page_config(
    page_title="MTG Deal Finder",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded"
)


def parse_card_input(card_text: str, ignore_set: bool = True) -> List[Card]:
    """
    Parse card input from text area.
    
    Args:
        card_text: Multi-line string with one card per line
        ignore_set: If True, set information is discarded (default: True)
    
    Returns:
        List of Card objects, deduplicated if ignore_set is True
    """
    cards = []
    for line in card_text.strip().split('\n'):
        if line.strip():
            card = parse_card_line(line, ignore_set=ignore_set)
            if card:
                cards.append(card)
    
    # Deduplicate cards if ignore_set is True
    if ignore_set:
        card_dict = {}
        for card in cards:
            key = card.name.lower()
            if key in card_dict:
                # Card already exists, add quantity
                card_dict[key].qty += card.qty
            else:
                # New card
                card_dict[key] = card
        cards = list(card_dict.values())
    
    return cards


def create_excel_download(offers: List[Offer]) -> bytes:
    """
    Create Excel file in memory for download.
    
    Args:
        offers: List of Offer objects
    
    Returns:
        Bytes of Excel file
    """
    df = create_dataframe(offers)
    
    # Sort by price
    if not df.empty:
        df = df.sort_values(by="Price", ascending=True)
    
    # Write to bytes buffer
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    
    return buffer.getvalue()


def main():
    """Main Streamlit application."""
    
    # Setup logging to capture in Streamlit
    setup_logging(debug=False)
    
    # Title and description
    st.title("🃏 MTG Deal Finder")
    st.markdown("""
    Find the best prices for Magic: The Gathering cards across multiple Canadian online stores.
    Paste your card list below and configure your search options in the sidebar.
    """)
    
    # Sidebar for options
    st.sidebar.header("⚙️ Search Options")
    
    # Store selection
    st.sidebar.subheader("Stores to Search")
    st.sidebar.markdown("Select which stores to search for cards:")
    
    store_options = {
        "FaceToFaceGames": "facetoface",
        "TopDeckHero": "topdeckhero"
    }
    
    selected_stores = st.sidebar.multiselect(
        "Stores",
        options=list(store_options.keys()),
        default=list(store_options.keys()),
        help="Choose which stores to search. More stores = better coverage but longer search time."
    )
    
    # TopDeckHero discount
    if "TopDeckHero" in selected_stores:
        topdeckhero_discount = st.sidebar.checkbox(
            "Apply TopDeckHero 20% Discount",
            value=False,
            help="TopDeckHero offers a 20% discount at checkout. Enable this to apply the discount to prices before comparison."
        )
    else:
        topdeckhero_discount = False
    
    # Selection strategy
    st.sidebar.subheader("Selection Strategy")
    st.sidebar.markdown("Choose how to select the best card from available offers:")
    
    strategy_display_names = {
        "cheapest": "Cheapest (any condition, any foiling)",
        "cheapest-foil": "Cheapest Foil",
        "cheapest-nonfoil": "Cheapest Non-Foil",
        "foil-first-cheapest": "Foil First (prefer foil, fallback to non-foil)",
        "best-condition": "Best Condition (cheapest Near Mint)",
        "blingiest": "Blingiest (most expensive foil)"
    }
    
    strategy_choice = st.sidebar.selectbox(
        "Strategy",
        options=list(strategy_display_names.keys()),
        format_func=lambda x: strategy_display_names[x],
        help="The strategy determines which card offer is selected when multiple options are available."
    )
    
    # Minimum quality
    st.sidebar.subheader("Quality Filter")
    st.sidebar.markdown("Filter cards by minimum quality/condition:")
    
    quality_display_names = {
        "none": "No restriction (any condition)",
        "mint": "Mint (M)",
        "nm": "Near Mint (NM)",
        "lp": "Lightly Played (LP)",
        "mp": "Moderately Played (MP)",
        "played": "Played (P)",
        "hp": "Heavily Played (HP)",
        "damaged": "Damaged"
    }
    
    min_quality_choice = st.sidebar.selectbox(
        "Minimum Quality",
        options=list(quality_display_names.keys()),
        format_func=lambda x: quality_display_names[x],
        help="Only show cards at this quality level or better. For example, 'Lightly Played' will show LP, NM, and Mint cards."
    )
    
    # Card parsing options
    st.sidebar.subheader("Card Parsing")
    ignore_set = st.sidebar.checkbox(
        "Ignore set information",
        value=True,
        help="When enabled, cards with the same name but different sets (e.g., 'Lightning Bolt (M11)' and 'Lightning Bolt (M10)') are treated as the same card. This allows finding the cheapest version across all sets."
    )
    
    # Cache options
    st.sidebar.subheader("Cache Settings")
    use_cache = st.sidebar.checkbox(
        "Enable caching",
        value=True,
        help="Cache search results for 24 hours to speed up repeated searches. Disable to always fetch fresh results."
    )
    
    # Main content area
    st.header("📝 Card List")
    st.markdown("""
    Enter your cards below, one per line. Supported formats:
    - Simple name: `Lightning Bolt`
    - With set: `Counterspell (7ED)`
    - With quantity: `Brainstorm x4` or `4x Brainstorm`
    - Combined: `Counterspell (7ED) x2`
    """)
    
    card_input = st.text_area(
        "Cards",
        height=300,
        placeholder="Lightning Bolt\nSol Ring\nCounterspell (7ED)\nBrainstorm x4",
        help="Enter one card per line. You can specify sets and quantities."
    )
    
    # Search button
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        search_button = st.button("🔍 Search for Cards", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.rerun()
    
    # Process search
    if search_button:
        if not card_input.strip():
            st.error("Please enter at least one card.")
            return
        
        if not selected_stores:
            st.error("Please select at least one store to search.")
            return
        
        # Parse cards
        with st.spinner("Parsing card list..."):
            cards = parse_card_input(card_input, ignore_set=ignore_set)
        
        if not cards:
            st.error("No valid cards found in input.")
            return
        
        st.success(f"Found {len(cards)} card(s) to search.")
        
        # Display parsed cards
        with st.expander("📋 Parsed Cards", expanded=False):
            for card in cards:
                set_info = f" ({card.set})" if card.set else ""
                qty_info = f" x{card.qty}" if card.qty > 1 else ""
                st.write(f"• {card.name}{set_info}{qty_info}")
        
        # Convert selected stores to filter string
        store_filter = ",".join([store_options[s] for s in selected_stores])
        
        # Search stores
        st.header("🔎 Searching Stores...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("Searching stores for cards...")
            card_offers = search_all_stores(
                cards,
                store_filter=store_filter,
                use_cache=use_cache,
                topdeckhero_discount=topdeckhero_discount
            )
            progress_bar.progress(50)
            
            # Calculate total offers
            total_offers = sum(len(offers) for offers in card_offers.values())
            
            if total_offers == 0:
                progress_bar.progress(100)
                status_text.text("Search complete.")
                st.warning("No offers found for any cards. Try different stores or check your card names.")
                return
            
            # Parse minimum quality
            min_quality = None
            if min_quality_choice != "none":
                min_quality = CardQuality.from_string(min_quality_choice)
            
            # Select best offers
            status_text.text("Selecting best offers...")
            selected_offers = select_best_offers(
                card_offers,
                cards,
                strategy_name=strategy_choice,
                min_quality=min_quality
            )
            
            progress_bar.progress(100)
            status_text.text("Search complete!")
            
            if not selected_offers:
                st.warning("No suitable offers found matching your criteria. Try relaxing your filters.")
                return
            
            # Display results
            st.header("✨ Results")
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Offers Found", total_offers)
            with col2:
                st.metric("Cards with Offers", len(selected_offers))
            with col3:
                total_cost = sum(offer.price for offer in selected_offers)
                st.metric("Total Cost", f"${total_cost:.2f}")
            
            # Results table
            st.subheader("Best Deals")
            df = create_dataframe(selected_offers)
            df = df.sort_values(by="Price", ascending=True)
            
            # Make URLs clickable
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "URL": st.column_config.LinkColumn("URL"),
                    "Price": st.column_config.NumberColumn("Price", format="$%.2f"),
                    "Foil": st.column_config.CheckboxColumn("Foil")
                }
            )
            
            # Download button
            st.subheader("📥 Download Results")
            excel_data = create_excel_download(selected_offers)
            st.download_button(
                label="Download Excel File",
                data=excel_data,
                file_name="mtg_deal_finder_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
        except Exception as e:
            progress_bar.progress(100)
            status_text.text("Error occurred during search.")
            st.error(f"An error occurred: {str(e)}")
            logging.exception("Error during search")


if __name__ == "__main__":
    main()
