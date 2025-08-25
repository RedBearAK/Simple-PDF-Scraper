# Simple PDF Scraper

A focused tool for extracting specific patterns of text from machine-generated PDF files using configurable search patterns and directional rules.

## Features

- **Targeted extraction**: Find text relative to keywords using directional rules
- **Flexible patterns**: Extract words, numbers, lines, or remaining text
- **Multiple processors**: Choose between pypdf (fast) and pdfplumber (advanced spacing)
- **Advanced spacing control**: Center-distance filtering to handle spurious spaces
- **Batch processing**: Handle multiple PDF files at once
- **TSV output**: Tab-separated format for reliable spreadsheet import
- **CLI-driven**: All configuration via command line arguments

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Simple-PDF-Scraper.git
cd Simple-PDF-Scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Extract a single pattern from one PDF:
```bash
python -m simple_pdf_scraper invoice.pdf --pattern "Invoice Number:right:2:number" --headers "Invoice"
```

### Tuning for Different Documents

Adjust adaptive thresholds for different document types:
```bash
# More conservative (fewer changes)
python -m simple_pdf_scraper invoice.pdf --min-space-ratio 1.5 --add-space-ratio 2.8 --pattern "Total:right:0:text"

# More aggressive (more spacing fixes)
python -m simple_pdf_scraper invoice.pdf --min-space-ratio 1.0 --add-space-ratio 3.5 --pattern "Invoice #:right:1:word"
```

### Fast Processing for Simple PDFs

For well-formatted PDFs without spacing issues, use pypdf for speed:
```bash
python -m simple_pdf_scraper invoice.pdf --processor pypdf --pattern "Total:right:0:text"
```

### Batch Processing

Process multiple PDFs with patterns from a file:
```bash
python -m simple_pdf_scraper *.pdf --patterns-file patterns.txt --output results.tsv
```

### Pattern Format

Patterns use the format: `keyword:direction:distance:extract_type`

- **keyword**: Text to search for (case-insensitive)
- **direction**: `left`, `right`, `above`, `below`
- **distance**: Number of words/lines to move from keyword
- **extract_type**: What to extract (`word`, `number`, `line`, `text`)

### Examples

```bash
# Extract invoice number (2 words to the right of "Invoice Number:")
"Invoice Number:right:2:number"

# Extract total amount (entire line below "Total:")
"Total:below:1:line"

# Extract company name (1 line above "Invoice")
"Invoice:above:1:line"

# Extract description (all remaining text after "Description:")
"Description:right:0:text"
```

### Patterns File

Create a text file with one pattern per line:
```
Invoice Number:right:1:word
Total Amount:right:1:number
Date:below:0:word
# Comments start with #
Description:right:0:text
```

## PDF Processing Options

### pdfplumber Processor (Default)
- **Font-size-aware** with adaptive thresholds
- **Character-level positioning** analysis
- **Center-distance filtering** to remove spurious spaces and add missing ones
- Excellent for **problematic PDFs** with spacing issues
- Automatically adapts to different font sizes
- Slightly slower but much more accurate

### pypdf Processor (Fast Alternative)  
- **Fast** and lightweight
- **Smart spacing patterns** to fix common concatenation issues
- Good for **simple, well-formatted PDFs** without major spacing problems
- Uses regex patterns to detect and fix issues like missing spaces between words/numbers

```bash
# Default: Use pdfplumber (recommended)
python -m simple_pdf_scraper invoice.pdf --pattern "Invoice:right:1:word"

# Fast alternative for simple PDFs
python -m simple_pdf_scraper invoice.pdf --processor pypdf --pattern "Total:right:0:text"

# Tune adaptive thresholds
python -m simple_pdf_scraper invoice.pdf --min-space-ratio 1.5 --add-space-ratio 2.8
```

### Command Line Options

```
positional arguments:
  files                 PDF file(s) to process (supports wildcards)

options:
  --pattern PATTERN     Single pattern (can be used multiple times)
  --patterns-file FILE  File containing patterns, one per line
  --output, -o FILE     Output file name (default: extracted_data.tsv)
  --headers HEADERS     Custom column headers
  --processor PROC      PDF processing backend (pdfplumber or pypdf)
  --min-space-ratio     Character spacing ratio to keep spaces (pdfplumber adaptive)
  --add-space-ratio     Character spacing ratio to add missing spaces (pdfplumber adaptive)
  --min-space-distance  Fixed minimum center-distance (pdfplumber legacy mode)
  --add-space-distance  Fixed distance threshold (pdfplumber legacy mode)
  --smart-spacing       Enable smart spacing patterns (pypdf)
  --verbose, -v         Show detailed processing information
```

## Architecture

The tool is designed with pluggable components:

- **Processors**: Different PDF text extraction backends:
  - `pypdf`: Fast extraction with smart spacing patterns for common concatenation issues
  - `pdfplumber`: Slower but more precise, uses character-level positioning and center-distance filtering to handle spurious spaces and missing spaces
- **Extractors**: Pattern-based text extraction with directional rules
- **Output**: TSV formatting with data cleaning

## Testing

Run all tests:
```bash
python tests/run_all_tests.py
```

Test specific features:
```bash
# Test center-distance filtering
python tests/test_center_distance_filtering.py your_pdf.pdf

# Compare processors
python tests/test_processor_comparison.py your_pdf.pdf
```

Or run individual test modules:
```bash
python tests/test_processors.py
python tests/test_extractors.py
python tests/test_integration.py
```

## Requirements

- Python 3.8+
- pdfplumber (primary processor, included in requirements.txt)
- pypdf (fast alternative, included in requirements.txt)

## Project Structure

```
Simple-PDF-Scraper/
├── simple_pdf_scraper/
│   ├── __init__.py
│   ├── __main__.py              # Entry point
│   ├── cli.py                   # Command line interface
│   ├── processors/              # PDF processing backends
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract processor
│   │   ├── pypdf_processor.py  # pypdf implementation
│   │   ├── pdfplumber_processor.py  # pdfplumber with center-distance filtering
│   │   └── pdfplumber_patterns.py  # Regex patterns for pdfplumber
│   ├── extractors/              # Pattern extraction
│   │   ├── __init__.py
│   │   └── pattern_extractor.py
│   └── output/                  # Output formatting
│       ├── __init__.py
│       └── tsv_writer.py
├── tests/                       # Test suite
│   ├── test_processors.py
│   ├── test_extractors.py
│   ├── test_integration.py
│   ├── test_center_distance_filtering.py
│   ├── test_processor_comparison.py
│   └── run_all_tests.py
├── requirements.txt
└── README.md
```

## License

GNU General Public License 3.0
