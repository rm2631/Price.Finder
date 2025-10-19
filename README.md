# MTG Deal Finder 💰🃏

A command-line tool that helps Magic: The Gathering players in Canada find the cheapest prices for missing cards across multiple online stores (currently supports FaceToFaceGames, with more stores coming soon).

You provide a simple text list of cards you need, and the tool searches each store, normalizes results, compares prices, and outputs an Excel spreadsheet with the best available deals.

## 🚀 Features

- **Scrapes multiple Canadian MTG stores** for card prices (currently FaceToFaceGames)
- **Modular architecture** — add new stores easily
- **Multiple selection strategies** — choose cheapest, best condition, foil/non-foil preferences
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

## 💻 Usage

### Basic Usage

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
  --store STORES          Comma-separated list of stores to search (e.g., facetoface)
  --strategy, -s STRATEGY Selection strategy for choosing best card (default: cheapest)
  --no-cache              Disable caching of search results
  --debug                 Enable debug logging
```

### Selection Strategies

The tool supports multiple strategies for selecting the best card offer:

- **cheapest** (default): Selects the lowest price regardless of condition or foil status
- **cheapest-nonfoil**: Selects the cheapest non-foil version
- **cheapest-foil**: Selects the cheapest foil version
- **best-condition**: Selects the cheapest Near Mint condition card
- **blingiest**: Selects the most expensive foil card (for "bling" factor)

Example using a strategy:
```bash
python -m mtg_deal_finder cards.txt --strategy best-condition --out nm_results.xlsx
```

### Input Format

The input file supports various formats:

- **Simple card name**: `Lightning Bolt`
- **Card with set**: `Counterspell (7ED)` or `Counterspell [Seventh Edition]`
- **Card with quantity**: `Brainstorm x4` or `4x Brainstorm`
- **Combined**: `Counterspell (7ED) x2`

### Output

The tool generates an Excel file with the following columns:

| Card | Set | Condition | Foil | Price | Store | URL |
|------|-----|-----------|------|-------|-------|-----|
| Lightning Bolt | Masters 25 | Near Mint | False | $2.49 | FaceToFaceGames | https://... |

The file is automatically sorted by price (cheapest first) and includes clickable URLs to product pages.


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
│   └── [future stores]     # Additional store implementations
├── compare.py               # Price aggregation and comparison logic
├── output.py                # Excel export logic
└── utils/
    ├── caching.py          # Optional caching layer
    └── normalization.py    # Fuzzy matching and validation
```

### 3. Common Data Models

- **Card** — represents a card with fields: `name`, `set` (optional), `qty` (default 1)
- **Offer** — represents a store offer with: `store`, `card`, `set`, `condition`, `price`, `url`, `foil`, and `availability`

Each store implements the same interface with a `search(card)` method returning a list of offers.
This makes adding new stores straightforward.

### 4. Scraping Strategy

- **API-first approach**: Use store APIs when available (e.g., FaceToFaceGames search API)
- **Static HTML fallback**: Use requests + BeautifulSoup for stores without APIs
- **Dynamic pages**: Use Playwright or Selenium in headless mode when necessary
- **Caching**: Cache results locally to avoid re-fetching identical pages
- **Rate limiting**: Add delays to stay polite and avoid rate limits

### 5. Selection Strategies

The tool supports multiple strategies for selecting the best offer from available options:

- **CheapestStrategy**: Select the lowest price regardless of condition or foil status
- **CheapestFoilStrategy**: Select the cheapest foil version
- **CheapestNonFoilStrategy**: Select the cheapest non-foil version  
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

- Add more stores (TopDeckHero, FusionGaming, 401Games, etc.)
- Implement multithreaded scraping for faster results
- Include shipping cost estimation
- Integrate login/cart linking
- Save results in a local SQLite database
- Build a web UI using Flask or FastAPI

## 📜 Legal & Ethical Notes

- Check each site's Terms of Service before scraping
- Use caching and delays to reduce server load
- This project is intended for personal use only

## 📝 License

MIT License — free for personal use, modification, and sharing.

Built by an MTG player, for MTG players.
