"""
aml_voyage_log_parser/__main__.py

Main entry point for voyage log parser package.
Orchestrates the parsing workflow and handles CLI interaction.
"""

import sys

from aml_voyage_log_parser.voyage_cli import (
    create_argument_parser,
    determine_output_formats,
    handle_output_error,
    handle_parsing_error,
    print_generation_info,
    print_output_info,
    print_processing_info,
    read_input_text,
    validate_input_text,
)
from aml_voyage_log_parser.voyage_debug import (
    show_preview,
    show_structural_debug,
)
from aml_voyage_log_parser.voyage_output import (
    get_delimiter_for_format,
    write_csv_file,
    write_to_stdout,
)
from aml_voyage_log_parser.voyage_parser_core import VoyageParser


def main():
    """
    Main entry point for the CLI application.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # Parse command line arguments
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Validate format selection
    try:
        formats = determine_output_formats(args)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    # Read input
    text = read_input_text(args.input)
    if not validate_input_text(text):
        return 1
    
    # Initialize parser
    voyage_parser = VoyageParser(debug=args.debug)
    
    # Show structural debug if requested
    if args.debug:
        show_structural_debug(text)
        print("\n" + "="*50 + "\n", file=sys.stderr)
    
    # Parse the text
    collection = voyage_parser.parse_text(text)
    
    # Show processing info
    print_processing_info(collection, args)
    
    # Check if any voyages were found
    if collection.voyage_count() == 0:
        return handle_parsing_error(collection)
    
    # Convert to records for output
    headers = collection.get_headers()
    records = collection.to_flat_records()
    
    # Show generation info
    print_generation_info(collection, args)
    
    # Handle preview mode
    if args.preview:
        show_preview(collection)
        return 0
    
    # Write output
    try:
        return write_outputs(args, headers, records, formats)
    except Exception as e:
        return handle_output_error(e)


def write_outputs(args, headers, records, formats):
    """
    Write output in requested formats.
    
    Args:
        args: Command line arguments
        headers (list): Column headers
        records (list): Data records
        formats (dict): Format flags
        
    Returns:
        int: Exit code
    """
    if args.output:
        return write_to_files(args, headers, records, formats)
    else:
        return write_to_stdout_format(args, headers, records, formats)


def write_to_files(args, headers, records, formats):
    """
    Write output to files.
    
    Args:
        args: Command line arguments
        headers (list): Column headers
        records (list): Data records
        formats (dict): Format flags
        
    Returns:
        int: Exit code
    """
    if formats['csv']:
        csv_file = f"{args.output}.csv"
        write_csv_file(csv_file, headers, records, delimiter=',')
        print_output_info(csv_file, "CSV", args)
    
    if formats['tsv']:
        tsv_file = f"{args.output}.tsv"
        write_csv_file(tsv_file, headers, records, delimiter='\t')
        print_output_info(tsv_file, "TSV", args)
    
    return 0


def write_to_stdout_format(args, headers, records, formats):
    """
    Write output to stdout in appropriate format.
    
    Args:
        args: Command line arguments
        headers (list): Column headers
        records (list): Data records
        formats (dict): Format flags
        
    Returns:
        int: Exit code
    """
    # Determine format for stdout
    if args.tsv:
        delimiter = '\t'
    else:
        delimiter = ','
    
    write_to_stdout(headers, records, delimiter)
    return 0


if __name__ == "__main__":
    sys.exit(main())

# End of file #