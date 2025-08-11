"""
aml_voyage_log_parser/voyage_cli.py

Command line interface for voyage log parser.
Handles argument parsing and user interaction.
"""

import argparse
import sys

from pathlib import Path


def create_argument_parser():
    """
    Create and configure the command line argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured parser
    """
    parser = argparse.ArgumentParser(
        description="Parse voyage log text dumps with structure-based approach",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse text file and create CSV/TSV
  python -m aml_voyage_log_parser voyage_dump.txt --output schedule
  
  # Parse from stdin and output to stdout as CSV
  python -m aml_voyage_log_parser < dump.txt > schedule.csv
  
  # Show structural debug info
  python -m aml_voyage_log_parser dump.txt --debug --preview
        """
    )
    
    # Input
    parser.add_argument('input', nargs='?', 
                       help='Input text file (use stdin if not provided)')
    
    # Output options
    parser.add_argument('--output', '-o',
                       help='Output filename base (extensions added automatically)')
    
    # Format options
    parser.add_argument('--csv', action='store_true',
                       help='Output CSV format (default if no format specified)')
    
    parser.add_argument('--tsv', action='store_true',
                       help='Output TSV format')
    
    parser.add_argument('--both', action='store_true',
                       help='Output both CSV and TSV formats')
    
    # Mode options
    parser.add_argument('--preview', action='store_true',
                       help='Show preview of parsed data without writing files')
    
    parser.add_argument('--debug', action='store_true',
                       help='Show detailed structural parsing debug information')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed processing information')
    
    return parser


def read_input_text(input_file):
    """
    Read text from file or stdin.
    
    Args:
        input_file (str or None): Input file path, or None for stdin
        
    Returns:
        str or None: Text content, or None on error
    """
    if input_file:
        return read_from_file(input_file)
    else:
        return read_from_stdin()


def read_from_file(file_path):
    """
    Read text from file.
    
    Args:
        file_path (str): Path to input file
        
    Returns:
        str or None: File content, or None on error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return None


def read_from_stdin():
    """
    Read text from stdin.
    
    Returns:
        str: Text from stdin
    """
    return sys.stdin.read()


def determine_output_formats(args):
    """
    Determine which output formats to generate.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        dict: Format flags {'csv': bool, 'tsv': bool}
        
    Raises:
        ValueError: If --output specified without format selection
    """
    # If using --output, require explicit format selection
    if args.output and not (args.csv or args.tsv or args.both):
        raise ValueError(
            "When using --output, please specify a format: --csv, --tsv, or --both\n"
            "Example: --output schedule --csv"
        )
    
    # If no --output specified, default to CSV for stdout
    output_csv = args.csv or args.both or (not args.tsv and not args.output)
    output_tsv = args.tsv or args.both
    
    return {
        'csv': output_csv,
        'tsv': output_tsv
    }


def validate_input_text(text):
    """
    Validate that input text is not empty.
    
    Args:
        text (str or None): Input text
        
    Returns:
        bool: True if text is valid
    """
    if not text or not text.strip():
        print("Error: No input text provided", file=sys.stderr)
        return False
    return True


def print_processing_info(collection, args):
    """
    Print processing information if verbose mode is enabled.
    
    Args:
        collection (VoyageCollection): Parsed voyage collection
        args: Command line arguments
    """
    if args.verbose or args.debug:
        print(f"Parsed {collection.voyage_count()} total voyages:", file=sys.stderr)
        
        # Show first few voyages
        for voyage in collection.voyages[:5]:
            print(f"  {voyage.region:10} {voyage.route:6} {voyage.port_count()} ports "
                  f"(Alias: '{voyage.alias}')", file=sys.stderr)
        
        if collection.voyage_count() > 5:
            print(f"  ... and {collection.voyage_count() - 5} more voyages", file=sys.stderr)
        
        print("", file=sys.stderr)


def print_generation_info(collection, args):
    """
    Print record generation information if verbose mode is enabled.
    
    Args:
        collection (VoyageCollection): Parsed voyage collection
        args: Command line arguments
    """
    if args.verbose:
        total_records = collection.total_ports()
        print(f"Generated {total_records} port records", file=sys.stderr)


def print_output_info(output_file, format_name, args):
    """
    Print output file information if verbose mode is enabled.
    
    Args:
        output_file (str): Path to output file
        format_name (str): Format name (CSV/TSV)
        args: Command line arguments
    """
    if args.verbose:
        print(f"{format_name} written to: {output_file}", file=sys.stderr)


def handle_parsing_error(collection):
    """
    Handle case where no voyages were parsed.
    
    Args:
        collection (VoyageCollection): Empty voyage collection
        
    Returns:
        int: Exit code
    """
    print("Error: No voyage data found in input", file=sys.stderr)
    return 1


def handle_output_error(error):
    """
    Handle output writing errors.
    
    Args:
        error (Exception): Output error
        
    Returns:
        int: Exit code
    """
    print(f"Error writing output: {error}", file=sys.stderr)
    return 1

# End of file #
