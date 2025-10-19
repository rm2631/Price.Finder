MTG Deal Finder 💰🃏

A command-line tool that helps Magic: The Gathering players in Canada find the cheapest prices for missing cards across multiple online stores (e.g., FaceToFaceGames and TopDeckHero).

You provide a simple text list of cards you need, and the tool searches each store, normalizes results, compares prices, and outputs an Excel spreadsheet with the best available deals.

🚀 Features

Scrapes multiple Canadian MTG stores for card prices

Modular architecture — add new stores easily

Uses consistent data models for clean comparison

Outputs a neatly formatted Excel file

Fast and parallelized scraping (optional)

Designed for CLI use — lightweight and scriptable

🏗️ Implementation Strategy
1. Input

The tool accepts a plain text file or multiline string where each line represents a card.

Example input
Lightning Bolt
Sol Ring
Counterspell (7ED)
Brainstorm x4

Each line is parsed into a structured Card object with attributes: name, set, and quantity.

2. Core Architecture

Folder structure:

mtg_deal_finder/
├── main.py (CLI entrypoint)
├── cards.py (Card parsing and normalization logic)
├── stores/
│ ├── base.py (Abstract StoreScraper interface)
│ ├── facetoface.py (FaceToFace scraper implementation)
│ └── topdeckhero.py (TopDeckHero scraper implementation)
├── compare.py (Price aggregation and comparison logic)
├── output.py (Excel export logic)
└── utils/
  ├── caching.py (Optional caching layer)
  └── normalization.py (Fuzzy matching and Scryfall validation)

3. Common Data Models

Card — represents a card with fields: name, set (optional), qty (default 1)
Offer — represents a store offer with: store, card, set, condition, price, and URL

Each store implements the same interface with a search(card) method returning a list of offers.
This makes adding new stores straightforward.

4. Scraping Strategy

Static HTML pages: use requests + BeautifulSoup

Dynamic pages: use Playwright or Selenium in headless mode

Cache results locally to avoid re-fetching identical pages

Add random delays to stay polite and avoid rate limits

5. Normalization

Ensure consistent formatting of card names, sets, and conditions:

Strip extra spaces, normalize capitalization and punctuation

Optionally validate via Scryfall API for canonical names and set codes

Handle foil and non-foil variants consistently

6. Price Comparison Logic

Aggregate all offers into a dataframe or list, then select the lowest price per card.
Group by card name and choose the cheapest offer for each.
This yields a clean, minimal list of best options across all stores.

7. Output

Results are exported to Excel using pandas with columns:

Card | Set | Qty | Best Price | Store | Condition | URL

Example output:
Sol Ring | CMR | 1 | 3.99 | FaceToFace | NM | https://...
Counterspell | 7ED | 1 | 1.25 | TopDeckHero | NM | https://...

8. CLI Usage

Example usage:

python mtg_deal_finder.py missing_cards.txt --out results.xlsx

Optional flags:

--store → filter which stores to include (e.g., facetoface,topdeckhero)
--no-cache → disable caching
--debug → print detailed scraping logs

9. Future Enhancements

Add more stores (FusionGaming, 401Games, etc.)

Implement multithreaded scraping

Include shipping cost estimation

Integrate login/cart linking

Save results in a local SQLite database

Build a web UI using Flask or FastAPI

10. Legal & Ethical Notes

Check each site’s Terms of Service before scraping

Use caching and delays to reduce server load

This project is intended for personal use only

🧰 Tech Stack

Language: Python 3.11+
Core libraries: requests, beautifulsoup4, pandas, openpyxl
Optional: playwright, fuzzywuzzy, scrython

📦 Example Workflow

Create a text file (e.g., missing.txt) with one card per line

Run: python mtg_deal_finder.py missing.txt --out deals.xlsx

Open the resulting Excel file to view the best prices

💡 Design Philosophy

Keep it simple, modular, and extensible:

Add new stores by subclassing one scraper class

Swap scraping backends easily

Focus on accurate data normalization and comparison

📜 License

MIT License — free for personal use, modification, and sharing.

Built by an MTG player, for MTG players.