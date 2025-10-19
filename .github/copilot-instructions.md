# GitHub Copilot Instructions for MTG Deal Finder

## Project Overview

MTG Deal Finder is a command-line tool that helps Magic: The Gathering players in Canada find the cheapest prices for cards across multiple online stores. The tool scrapes store websites/APIs, normalizes results, compares prices, and outputs an Excel spreadsheet with the best available deals.

## Architecture

### Core Components

1. **CLI Entry Point** (`mtg_deal_finder/main.py`): Handles argument parsing, logging, and orchestrates the workflow
2. **Data Models** (`mtg_deal_finder/cards.py`): Defines `Card` and `Offer` classes
3. **Store Scrapers** (`mtg_deal_finder/stores/`): Modular scrapers implementing the `StoreScraper` interface
4. **Selection Strategies** (`mtg_deal_finder/strategies.py`): Different algorithms for selecting the best offer
5. **Output Handler** (`mtg_deal_finder/output.py`): Excel export functionality
6. **Utilities** (`mtg_deal_finder/utils/`): Caching and normalization helpers

### Design Patterns

- **Strategy Pattern**: Selection strategies (cheapest, best-condition, etc.) implement a common interface
- **Template Method**: Store scrapers extend `StoreScraper` base class
- **Data Models**: Consistent `Card` and `Offer` objects across the codebase

## Coding Conventions

### Python Style
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes (Google style)
- Maximum line length: 100 characters
- Use f-strings for string formatting

### File Organization
- Keep stores in `stores/` subdirectory
- Each store scraper is a separate file (e.g., `facetoface.py`, `topdeckhero.py`)
- Utility functions in `utils/` subdirectory
- Keep data models simple and in `cards.py`

### Naming Conventions
- Classes: PascalCase (e.g., `FaceToFaceScraper`, `CheapestStrategy`)
- Functions/methods: snake_case (e.g., `parse_card_line`, `search_all_stores`)
- Constants: UPPER_SNAKE_CASE (e.g., `AVAILABLE_STRATEGIES`, `CACHE_TTL`)
- Private methods: prefix with single underscore (e.g., `_normalize_price`)

## Dependencies

### Core Dependencies
- **requests**: HTTP requests for API calls and web scraping
- **beautifulsoup4**: HTML parsing (for stores without APIs)
- **pandas**: Data manipulation and Excel export
- **openpyxl**: Excel file generation

### Future Dependencies (commented out in requirements.txt)
- **playwright**: For dynamic page scraping (when needed)
- **fuzzywuzzy**: For fuzzy string matching in card names
- **scrython**: Scryfall API wrapper for card validation

## Adding New Features

### Adding a New Store Scraper

1. Create a new file in `mtg_deal_finder/stores/` (e.g., `newstore.py`)
2. Import and extend `StoreScraper` from `base.py`
3. Implement the `search(card: Card) -> List[Offer]` method
4. Add the scraper to the `scrapers` dictionary in `main.py`
5. Use caching via `self.cache` if `use_cache` is enabled

Example:
```python
from mtg_deal_finder.stores.base import StoreScraper
from mtg_deal_finder.cards import Card, Offer

class NewStoreScraper(StoreScraper):
    def search(self, card: Card) -> List[Offer]:
        # Implementation here
        pass
```

### Adding a New Selection Strategy

1. Create a new class in `strategies.py` that implements `SelectionStrategy`
2. Implement the `select(offers: List[Offer]) -> Offer` method
3. Add a `get_name()` method that returns a descriptive name
4. Register the strategy in the `AVAILABLE_STRATEGIES` dictionary

Example:
```python
class BestValueStrategy(SelectionStrategy):
    def select(self, offers: List[Offer]) -> Offer:
        # Implementation here
        pass
    
    def get_name(self) -> str:
        return "Best Value (price/condition ratio)"
```

## Testing and Development

### Running the Tool
```bash
# Install dependencies
pip install -r requirements.txt

# Run with a card list
python -m mtg_deal_finder cards.txt

# Enable debug logging
python -m mtg_deal_finder cards.txt --debug

# Use specific strategy
python -m mtg_deal_finder cards.txt --strategy best-condition
```

### Debugging
- Use `--debug` flag for detailed logging
- Check cached results in the cache directory
- Use `--no-cache` to bypass caching during development

### Common Development Tasks
- **Clear cache**: Delete cache files in the cache directory
- **Test single store**: Use `--store storename` to test one scraper
- **Validate output**: Check generated Excel files for correct formatting

## Important Design Decisions

### Caching
- Search results are cached for 24 hours by default
- Cache key is based on card name and store
- Caching can be disabled with `--no-cache` flag
- Cache is implemented in `utils/caching.py`

### Price Comparison
- All prices are stored as float values (in CAD)
- Prices are compared after normalization
- Selection strategies operate on normalized `Offer` objects

### Error Handling
- Store scraping errors are logged but don't stop the entire search
- Missing cards result in warnings, not errors
- Failed Excel export is treated as a critical error

### Scraping Strategy
- **API-first**: Use store APIs when available (e.g., FaceToFaceGames)
- **Static HTML**: Use BeautifulSoup for stores without APIs (e.g., TopDeckHero)
- **Rate limiting**: Add delays between requests to be polite
- **Pagination**: Scrape up to 2 pages per store for better coverage

## Card Input Format

The tool supports several input formats:
- Simple name: `Lightning Bolt`
- With set code: `Counterspell (7ED)` or `Counterspell [Seventh Edition]`
- With quantity: `Brainstorm x4` or `4x Brainstorm`
- Combined: `Counterspell (7ED) x2`

Parsing logic is in `main.py` (`parse_card_line` function).

## Output Format

Excel files contain the following columns:
- **Card**: Card name
- **Set**: Set code or name
- **Condition**: Card condition (e.g., Near Mint, Lightly Played)
- **Foil**: Boolean indicating if the card is foil
- **Price**: Price in CAD
- **Store**: Store name
- **URL**: Clickable link to the product page

## Future Enhancements

When implementing new features, consider:
- Maintaining backward compatibility with existing card input format
- Adding new strategies without breaking existing ones
- Keeping store scrapers independent and modular
- Following the existing logging and error handling patterns
- Updating README.md with new features

## Performance Considerations

- Use caching to avoid redundant API calls
- Consider multithreading for store searches (future enhancement)
- Limit pagination to avoid excessive scraping
- Implement rate limiting to respect store servers

## Legal and Ethical Notes

- Always respect store Terms of Service
- Use caching and delays to reduce server load
- This tool is for personal use only
- Avoid excessive scraping that could impact store performance
