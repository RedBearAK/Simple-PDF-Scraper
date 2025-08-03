"""
Command line interface for Simple PDF Scraper.

File: simple_pdf_scraper/cli.py
"""

import sys
import glob
import argparse

from pathlib import Path

from simple_pdf_scraper.output.tsv_writer import TSVWriter
from simple_pdf_scraper.processors.pypdf_processor import PyPDFProcessor
from simple_pdf_scraper.extractors.pattern_extractor import PatternExtractor


def parse_pattern(pattern_str):
    """
    Parse pattern string in format: keyword:direction:distance:extract_type
    
    Examples:
        "Invoice Number:right:2:number" - Find number 2 words to the right of "Invoice Number"
        "Total:below:1:line" - Extract entire line 1 line below "Total"
        "Date:left:3:word" - Extract single word 3 words to the left of "Date"
    """
    parts = pattern_str.split(':')
    if len(parts) != 4:
        raise ValueError(f"Pattern must have format 'keyword:direction:distance:extract_type', got: {pattern_str}")
    
    keyword, direction, distance, extract_type = parts
    
    try:
        distance = int(distance)
    except ValueError:
        raise ValueError(f"Distance must be a number, got: {distance}")
    
    if direction not in ['left', 'right', 'above', 'below']:
        raise ValueError(f"Direction must be one of: left, right, above, below, got: {direction}")
    
    if extract_type not in ['word', 'number', 'line', 'text']:
        raise ValueError(f"Extract type must be one of: word, number, line, text, got: {extract_type}")
    
    return {
        'keyword': keyword.strip(),
        'direction': direction,
        'distance': distance,
        'extract_type': extract_type
    }


def parse_patterns_file(file_path):
    """Parse patterns from a file, one pattern per line."""
    patterns = []
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                try:
                    patterns.append(parse_pattern(line))
                except ValueError as e:
                    print(f"Error in patterns file line {line_num}: {e}", file=sys.stderr)
                    return None
    return patterns


def expand_file_paths(file_patterns):
    """Expand file patterns and return list of actual PDF files."""
    pdf_files = []
    for pattern in file_patterns:
        if '*' in pattern or '?' in pattern:
            matches = glob.glob(pattern)
            pdf_files.extend([f for f in matches if f.lower().endswith('.pdf')])
        else:
            if pattern.lower().endswith('.pdf') and Path(pattern).exists():
                pdf_files.append(pattern)
            else:
                print(f"Warning: Skipping non-PDF or non-existent file: {pattern}", file=sys.stderr)
    
    return sorted(set(pdf_files))  # Remove duplicates and sort


def create_argument_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="simple-pdf-scraper",
        description="Extract targeted text data from PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dump all text from PDF (default with no patterns)
  python -m simple_pdf_scraper invoice.pdf
  
  # Batch text dump to single TSV file
  python -m simple_pdf_scraper *.pdf --dump-text --output all_content.tsv
  
  # Batch text dump to separate TSV files (invoice1.pdf → invoice1.tsv)
  python -m simple_pdf_scraper *.pdf --dump-text --split-output
  
  # Single file with inline pattern
  python -m simple_pdf_scraper invoice.pdf --pattern "Invoice Number:right:2:number" --headers "Invoice"
  
  # Batch pattern extraction to single file
  python -m simple_pdf_scraper *.pdf --patterns-file patterns.txt --output results.tsv
  
  # Batch pattern extraction to separate files  
  python -m simple_pdf_scraper *.pdf --patterns-file patterns.txt --split-output

Pattern format: keyword:direction:distance:extract_type
  keyword:       Text to search for
  direction:     left, right, above, below
  distance:      Number of words/lines to move
  extract_type:  word, number, line, text
        """
    )
    
    parser.add_argument('files', nargs='+', help='PDF file(s) to process (supports wildcards)')
    
    # Pattern specification
    pattern_group = parser.add_mutually_exclusive_group(required=False)
    pattern_group.add_argument('--pattern', action='append', 
                              help='Single pattern (can be used multiple times)')
    pattern_group.add_argument('--patterns-file', 
                              help='File containing patterns, one per line')
    pattern_group.add_argument('--dump-text', action='store_true',
                              help='Extract and output all text content (default if no patterns given)')
    
    # Output options
    parser.add_argument('--output', '-o', default='extracted_data.tsv',
                       help='Output file name (default: extracted_data.tsv, ignored with --split-output)')
    parser.add_argument('--split-output', action='store_true',
                       help='Create separate TSV files for each PDF (invoice.pdf → invoice.tsv)')
    parser.add_argument('--headers', nargs='+',
                       help='Custom column headers (default: auto-generated from patterns)')
    
    # Processing options
    parser.add_argument('--processor', default='pypdf', choices=['pypdf'],
                       help='PDF processing backend (default: pypdf)')
    
    # Verbosity
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed processing information')
    
    return parser


def main():
    """Main entry point for the CLI."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Determine mode: text dump or pattern extraction
    text_dump_mode = args.dump_text or (not args.pattern and not args.patterns_file)
    
    patterns = []
    if not text_dump_mode:
        # Parse patterns for extraction mode
        if args.pattern:
            try:
                patterns = [parse_pattern(p) for p in args.pattern]
            except ValueError as e:
                print(f"Error parsing pattern: {e}", file=sys.stderr)
                return 1
        else:
            patterns = parse_patterns_file(args.patterns_file)
            if patterns is None:
                return 1
        
        if not patterns:
            print("Error: No valid patterns specified", file=sys.stderr)
            return 1
    
    # Expand file paths
    pdf_files = expand_file_paths(args.files)
    if not pdf_files:
        print("Error: No PDF files found", file=sys.stderr)
        return 1
    
    if args.verbose:
        print(f"Found {len(pdf_files)} PDF files to process")
        if text_dump_mode:
            print("Mode: Text dump")
        else:
            print(f"Mode: Pattern extraction with {len(patterns)} patterns")
    
    # Initialize components
    if args.processor == 'pypdf':
        processor = PyPDFProcessor()
    else:
        print(f"Error: Unknown processor: {args.processor}", file=sys.stderr)
        return 1
    
    if text_dump_mode:
        # Text dump mode: extract all text
        headers = ['filename', 'page', 'text_content']
        
        if args.split_output:
            # Create separate TSV files for each PDF
            writer = TSVWriter()
            processed_files = 0
            
            for pdf_file in pdf_files:
                if args.verbose:
                    print(f"Processing: {pdf_file}")
                
                try:
                    pages = processor.extract_pages(pdf_file)
                    pdf_results = []
                    
                    for page_num, page_text in enumerate(pages, 1):
                        pdf_results.append([pdf_file, page_num, page_text])
                    
                    if pdf_results:
                        # Create output filename based on PDF name
                        pdf_path = Path(pdf_file)
                        output_file = pdf_path.with_suffix('.tsv').name
                        writer.write_results(output_file, headers, pdf_results)
                        
                        if args.verbose:
                            print(f"  Wrote {len(pdf_results)} pages to {output_file}")
                        
                        processed_files += 1
                        
                except Exception as e:
                    print(f"Error processing {pdf_file}: {e}", file=sys.stderr)
                    continue
            
            if processed_files > 0:
                if args.verbose:
                    print(f"Successfully processed {processed_files}/{len(pdf_files)} files")
                return 0
            else:
                print("No files could be processed", file=sys.stderr)
                return 1
        
        else:
            # Single TSV file mode
            all_results = []
            
            for pdf_file in pdf_files:
                if args.verbose:
                    print(f"Processing: {pdf_file}")
                
                try:
                    pages = processor.extract_pages(pdf_file)
                    for page_num, page_text in enumerate(pages, 1):
                        all_results.append([pdf_file, page_num, page_text])
                        
                except Exception as e:
                    print(f"Error processing {pdf_file}: {e}", file=sys.stderr)
                    continue
    
    else:
        # Pattern extraction mode
        extractor = PatternExtractor()
        
        # Set up column headers
        if args.headers:
            if len(args.headers) != len(patterns):
                print(f"Error: Number of headers ({len(args.headers)}) must match number of patterns ({len(patterns)})", file=sys.stderr)
                return 1
            headers = ['filename', 'page'] + args.headers
        else:
            headers = ['filename', 'page'] + [p['keyword'] for p in patterns]
        
        if args.split_output:
            # Create separate TSV files for each PDF
            writer = TSVWriter()
            processed_files = 0
            
            for pdf_file in pdf_files:
                if args.verbose:
                    print(f"Processing: {pdf_file}")
                
                try:
                    pages = processor.extract_pages(pdf_file)
                    pdf_results = []
                    
                    for page_num, page_text in enumerate(pages, 1):
                        row = [pdf_file, page_num]
                        
                        for pattern in patterns:
                            result = extractor.extract_pattern(page_text, pattern)
                            row.append(result if result is not None else '')
                        
                        # Only add row if at least one pattern matched
                        if any(cell != '' for cell in row[2:]):
                            pdf_results.append(row)
                    
                    if pdf_results:
                        # Create output filename based on PDF name
                        pdf_path = Path(pdf_file)
                        output_file = pdf_path.with_suffix('.tsv').name
                        writer.write_results(output_file, headers, pdf_results)
                        
                        if args.verbose:
                            print(f"  Wrote {len(pdf_results)} matching rows to {output_file}")
                        
                        processed_files += 1
                    
                except Exception as e:
                    print(f"Error processing {pdf_file}: {e}", file=sys.stderr)
                    continue
            
            if processed_files > 0:
                if args.verbose:
                    print(f"Successfully processed {processed_files}/{len(pdf_files)} files")
                return 0
            else:
                print("No matching patterns found in any files", file=sys.stderr)
                return 1
        
        else:
            # Single TSV file mode for pattern extraction
            all_results = []
            
            for pdf_file in pdf_files:
                if args.verbose:
                    print(f"Processing: {pdf_file}")
                
                try:
                    pages = processor.extract_pages(pdf_file)
                    for page_num, page_text in enumerate(pages, 1):
                        row = [pdf_file, page_num]
                        
                        for pattern in patterns:
                            result = extractor.extract_pattern(page_text, pattern)
                            row.append(result if result is not None else '')
                        
                        # Only add row if at least one pattern matched
                        if any(cell != '' for cell in row[2:]):
                            all_results.append(row)
                    
                except Exception as e:
                    print(f"Error processing {pdf_file}: {e}", file=sys.stderr)
                    continue
    
    # Write results for single TSV file modes
    if not args.split_output:
        if all_results:
            writer = TSVWriter()
            writer.write_results(args.output, headers, all_results)
            
            if args.verbose:
                if text_dump_mode:
                    print(f"Text dump completed: {len(all_results)} pages extracted")
                else:
                    print(f"Pattern extraction completed: {len(all_results)} matching rows")
                print(f"Results written to: {args.output}")
        else:
            if text_dump_mode:
                print("No text could be extracted from any files", file=sys.stderr)
            else:
                print("No data extracted from any files", file=sys.stderr)
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

# End of file #
