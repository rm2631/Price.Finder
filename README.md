# MTG Deal Finder 💰🃏

A command-line tool that helps Magic: The Gathering players in Canada find the cheapest prices for missing cards across multiple online stores (currently supports FaceToFaceGames, TopDeckHero, TopDeckBoucherville, TopDeckJoliette, and MTGJeuxJubes, with more stores coming soon).

You provide a simple text list of cards you need, and the tool searches each store, normalizes results, compares prices, and outputs an Excel spreadsheet with the best available deals.

## 🚀 Features

- **Scrapes multiple Canadian MTG stores** for card prices (FaceToFaceGames, TopDeckHero, TopDeckBoucherville, TopDeckJoliette, and MTGJeuxJubes)
- **Automatic caching** — search results are cached for 24 hours to improve performance
- **Multi-page support** — scrapes up to 2 pages of results per store for better coverage
- **Modular architecture** — add new stores easily
- **Multiple selection strategies** — choose cheapest, best condition, foil/non-foil preferences
- **Quality filtering** — set minimum quality requirements to avoid buying cards in poor condition
- **Uses consistent data models** for clean comparison
- **Outputs a neatly formatted Excel file** with all details
- **Fast and efficient** — uses store APIs when available
- **Designed for CLI use** — lightweight and scriptable

## 📦 Installation

1. Clone this repository:
```bash
git clone https://github.com/rm2631/Price.Finder.git
cd Price.Finder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

**Launch the web interface:**
```bash
streamlit run streamlit_app.py
```

Your browser will automatically open to the MTG Deal Finder interface. Simply paste your card list and click "Search for Cards"!

## 💻 Usage

### Web UI (Recommended)

The easiest way to use MTG Deal Finder is through the web interface:

```bash
streamlit run streamlit_app.py
```

This will open a browser window where you can:
- Paste your card list directly (no file needed)
- Configure all search options through an intuitive interface
- View results in an interactive table
- Download results as Excel directly in your browser

All CLI options are available in the UI with helpful tooltips explaining each option.

### Command-Line Usage

Create a text file with one card per line (e.g., `cards.txt`):
```
Lightning Bolt
Sol Ring
Counterspell (7ED)
Brainstorm x4
```

Run the tool:
```bash
python -m mtg_deal_finder cards.txt --out results.xlsx
```

### Command-Line Options

```bash
python -m mtg_deal_finder <input_file> [options]

Options:
  --out, -o FILE          Output Excel file path (default: results.xlsx)
  --store STORES          Comma-separated list of stores to search (e.g., facetoface,topdeckhero,topdeckboucherville,topdeckjoliette,mtgjeuxjubes)
  --strategy, -s STRATEGY Selection strategy for choosing best card (default: cheapest)
  --min-quality, -q QUAL  Minimum card quality/condition to consider (e.g., nm, lp, mp)
  --topdeck-discount      Apply TopDeck's 20% checkout discount to prices (applies to TopDeckHero, TopDeckBoucherville, TopDeckJoliette, and MTGJeuxJubes)
  --no-cache              Disable caching of search results
  --debug                 Enable debug logging
```

### Minimum Quality Filter

You can filter results to only show cards that meet a minimum quality requirement:

```bash
# Only show Near Mint or better cards
python -m mtg_deal_finder cards.txt --min-quality nm

# Only show Lightly Played or better cards
python -m mtg_deal_finder cards.txt --min-quality lp
```

**Quality levels** (from best to worst):
- **mint** or **m**: Mint condition
- **nm**: Near Mint
- **lp**: Lightly Played
- **mp**: Moderately Played
- **played** or **pl**: Played
- **hp**: Heavily Played
- **damaged** or **dmg**: Damaged

When you specify a minimum quality, only cards at that quality level or better will be considered. For example, `--min-quality lp` will show Near Mint and Lightly Played cards, but filter out Moderately Played, Played, Heavily Played, and Damaged cards.

### Selection Strategies

The tool supports multiple strategies for selecting the best card offer:

- **cheapest** (default): Selects the lowest price regardless of condition or foil status
- **cheapest-nonfoil**: Selects the cheapest non-foil version
- **cheapest-foil**: Selects the cheapest foil version
- **foil-first-cheapest**: Prefers foil cards - selects the cheapest foil if available, otherwise falls back to the cheapest non-foil
- **best-condition**: Selects the cheapest Near Mint condition card
- **blingiest**: Selects the most expensive foil card (for "bling" factor)

All strategies respect the minimum quality filter if specified.

Example using a strategy:
```bash
python -m mtg_deal_finder cards.txt --strategy best-condition --out nm_results.xlsx
```

Example combining strategy with minimum quality:
```bash
# Get the cheapest non-foil card, but only LP or better
python -m mtg_deal_finder cards.txt --strategy cheapest-nonfoil --min-quality lp
```

### TopDeck Discount

TopDeck stores (TopDeckHero, TopDeckBoucherville, and TopDeckJoliette) offer a 20% discount at checkout. You can apply this discount to TopDeck prices using the `--topdeck-discount` flag:

```bash
# Apply the 20% discount to TopDeck prices
python -m mtg_deal_finder cards.txt --topdeck-discount
```

When this flag is enabled, all TopDeck store prices (stores with "topdeck" in their domain) will be reduced by 20% before comparison, giving you a more accurate view of the final price you'll pay.

**Example:**
- Without discount: TopDeck price is $10.00
- With discount: TopDeck price is $8.00 (20% off)

This makes it easier to compare TopDeck prices with other stores that don't offer a checkout discount.

### Store Filtering

You can limit your search to specific stores:

```bash
# Search only TopDeckBoucherville
python -m mtg_deal_finder cards.txt --store topdeckboucherville

# Search only FaceToFaceGames
python -m mtg_deal_finder cards.txt --store facetoface

# Search multiple specific stores
python -m mtg_deal_finder cards.txt --store facetoface,topdeckhero,mtgjeuxjubes

# Search all stores (default)
python -m mtg_deal_finder cards.txt
```

### Caching

Search results are automatically cached for 24 hours to improve performance on repeated searches. Cached results older than 24 hours are automatically deleted when a new search is performed, ensuring you always get fresh pricing data. To disable caching:

```bash
python -m mtg_deal_finder cards.txt --no-cache
```

### Input Format

The input file supports various formats:

- **Simple card name**: `Lightning Bolt`
- **Card with set**: `Counterspell (7ED)` or `Counterspell [Seventh Edition]`
- **Card with quantity**: `Brainstorm x4` or `4x Brainstorm`
- **Combined**: `Counterspell (7ED) x2`

### Output

The tool generates an Excel file with the following columns:

| Selected | Query | Card | Set | Condition | Foil | Price | Quantity | Store | URL |
|----------|-------|------|-----|-----------|------|-------|----------|-------|-----|
| ✓ | Lightning Bolt | Lightning Bolt | Masters 25 | Played | False | $1.99 | 1 | FaceToFaceGames | https://... |
| | Lightning Bolt | Lightning Bolt | Premium Deck | Near Mint | False | $2.49 | 1 | FaceToFaceGames | https://... |
| | Lightning Bolt | Lightning Bolt | The List | Played | False | $1.99 | 0 | FaceToFaceGames | https://... |

**Key features:**
- **All offers are included** - The Excel file contains every available offer found across all stores, not just the selected ones
- **Selected offers are marked** - The "Selected" column shows a ✓ for offers chosen by your selection strategy
- **Quantity indicates availability** - 1 means in stock, 0 means out of stock
- **Sorted for easy review** - Results are sorted by card name, selected offers first, then by price

This allows you to review all available options and understand why a particular offer was selected, making it easy to choose an alternative if needed.


## 🏗️ Implementation Strategy

### 1. Input

The tool accepts a plain text file or multiline string where each line represents a card.

Example input:
```
Lightning Bolt
Sol Ring
Counterspell (7ED)
Brainstorm x4
```

Each line is parsed into a structured `Card` object with attributes: `name`, `set`, and `quantity`.

### 2. Core Architecture

Folder structure:

```
mtg_deal_finder/
├── main.py                  # CLI entrypoint and orchestration
├── cards.py                 # Card and Offer data models
├── strategies.py            # Selection strategies for choosing best offers
├── stores/
│   ├── base.py             # Abstract StoreScraper interface
│   ├── facetoface.py       # FaceToFace scraper (uses store API)
│   ├── topdeckhero.py      # TopDeckHero scraper (HTML scraping)
│   └── [future stores]     # Additional store implementations
├── compare.py               # Price aggregation and comparison logic
├── output.py                # Excel export logic
└── utils/
    ├── caching.py          # Local caching layer (24-hour TTL)
    └── normalization.py    # Fuzzy matching and validation
```

### 3. Common Data Models

- **Card** — represents a card with fields: `name`, `set` (optional), `qty` (default 1)
- **Offer** — represents a store offer with: `store`, `card`, `set`, `condition`, `price`, `url`, `foil`, and `availability`

Each store implements the same interface with a `search(card)` method returning a list of offers.
This makes adding new stores straightforward.

### 4. Scraping Strategy

- **API-first approach**: Use store APIs when available (e.g., FaceToFaceGames search API)
- **Static HTML fallback**: Use requests + BeautifulSoup for stores without APIs (e.g., TopDeckHero)
- **Dynamic pages**: Use Playwright or Selenium in headless mode when necessary (reserved for future stores)
- **Caching**: Cache results locally (24-hour TTL) to avoid re-fetching identical pages
- **Pagination**: Scrape up to 2 pages per store for better coverage
- **Rate limiting**: Add delays between page requests to stay polite and avoid rate limits

### 5. Selection Strategies

The tool supports multiple strategies for selecting the best offer from available options:

- **CheapestStrategy**: Select the lowest price regardless of condition or foil status
- **CheapestFoilStrategy**: Select the cheapest foil version
- **CheapestNonFoilStrategy**: Select the cheapest non-foil version
- **FoilFirstCheapestStrategy**: Prefer foil cards - select the cheapest foil if available, otherwise the cheapest non-foil
- **BestConditionStrategy**: Select the cheapest Near Mint condition card
- **BlingiestStrategy**: Select the most expensive foil card

Each strategy implements a `select(offers)` method that returns the best offer according to its criteria. This design makes it easy to add new strategies in the future (e.g., "cheapest within a specific set", "best condition within budget", etc.).

### 6. Normalization

Ensure consistent formatting of card names, sets, and conditions:

- Strip extra spaces, normalize capitalization and punctuation
- Optionally validate via Scryfall API for canonical names and set codes
- Handle foil and non-foil variants consistently
- Filter out non-English cards

### 7. Price Comparison Logic

Aggregate all offers from multiple stores, then use the selected strategy to choose the best offer for each card. This yields a clean, minimal list of best options across all stores.

### 8. Output

Results are exported to Excel using pandas with columns:

| Card | Set | Condition | Foil | Price | Store | URL |
|------|-----|-----------|------|-------|-------|-----|
| Lightning Bolt | Masters 25 | Near Mint | False | $2.49 | FaceToFaceGames | https://... |

The file is automatically sorted by price (cheapest first) and includes clickable URLs to product pages.

## 🧰 Tech Stack

- **Language**: Python 3.11+
- **Core libraries**: requests, beautifulsoup4, pandas, openpyxl
- **Optional**: playwright, fuzzywuzzy, scrython

## 📦 Example Workflow

1. Create a text file (e.g., `missing.txt`) with one card per line
2. Run: `python -m mtg_deal_finder missing.txt --out deals.xlsx`
3. Open the resulting Excel file to view the best prices

## 💡 Design Philosophy

Keep it simple, modular, and extensible:

- Add new stores by subclassing the `StoreScraper` class
- Add new selection strategies by implementing the `SelectionStrategy` interface
- Swap scraping backends easily
- Focus on accurate data normalization and comparison

## 🚀 Future Enhancements

- Add more stores (FusionGaming, 401Games, etc.)
- Implement multithreaded scraping for faster results
- Include shipping cost estimation
- Integrate login/cart linking
- Save results in a local SQLite database

## 📜 Legal & Ethical Notes

- Check each site's Terms of Service before scraping
- Use caching and delays to reduce server load
- This project is intended for personal use only

## 📝 License

MIT License — free for personal use, modification, and sharing.

Built by an MTG player, for MTG players.
