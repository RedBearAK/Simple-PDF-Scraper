# Simple PDF Scraper

A focused tool for extracting specific patterns of text from machine-generated PDF files using configurable search patterns and directional rules.

## Features

- **Targeted extraction**: Find text relative to keywords using directional rules
- **Flexible patterns**: Extract words, numbers, lines, or remaining text
- **Pluggable processors**: Easily swap PDF processing backends
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

### Command Line Options

```
positional arguments:
  files                 PDF file(s) to process (supports wildcards)

options:
  --pattern PATTERN     Single pattern (can be used multiple times)
  --patterns-file FILE  File containing patterns, one per line
  --output, -o FILE     Output file name (default: extracted_data.tsv)
  --headers HEADERS     Custom column headers
  --processor PROC      PDF processing backend (default: pypdf)
  --verbose, -v         Show detailed processing information
```

## Architecture

The tool is designed with pluggable components:

- **Processors**: Different PDF text extraction backends (`pypdf`, future: `pdfplumber`, `PyMuPDF`)
- **Extractors**: Pattern-based text extraction with directional rules
- **Output**: TSV formatting with data cleaning

## Testing

Run all tests:
```bash
python tests/run_all_tests.py
```

Or run individual test modules:
```bash
python tests/test_processors.py
python tests/test_extractors.py
python tests/test_integration.py
```

Tests can also be run with pytest:
```bash
pytest tests/
```

## Requirements

- Python 3.8+
- pypdf

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
│   │   └── pypdf_processor.py  # pypdf implementation
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
│   └── run_all_tests.py
├── requirements.txt
└── README.md
```

## License

GNU General Public License 3.0
