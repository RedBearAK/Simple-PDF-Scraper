"""
aml_voyage_log_parser/voyage_output.py

CSV/TSV output formatting and writing functions.
Handles clean data export with proper formatting preservation.
"""

import csv
import sys

from aml_voyage_log_parser.voyage_patterns import datetime_combined_rgx


def clean_cell_for_csv(value):
    """
    Clean cell value for CSV output.
    
    Args:
        value: Raw cell value
        
    Returns:
        str: Cleaned value suitable for CSV/TSV
    """
    if value is None or value == '':
        return ''
    
    str_value = str(value)
    
    # For date/time values, ensure consistent format
    if datetime_combined_rgx.match(str_value):
        # Return as-is - properly formatted date/time from PDF
        return str_value
    
    # For other values, clean problematic characters
    return str_value.replace('\t', ' ').replace('\n', ' ').replace('\r', '')


def write_csv_file(filename, headers, records, delimiter=','):
    """
    Write records to CSV/TSV file with proper formatting.
    
    Args:
        filename (str): Output file path
        headers (list): Column headers
        records (list): List of data rows
        delimiter (str): Field delimiter (',' or '\t')
    """
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        
        # Clean records to preserve formatting
        for record in records:
            cleaned_record = [clean_cell_for_csv(cell) for cell in record]
            writer.writerow(cleaned_record)


def write_to_stdout(headers, records, delimiter=','):
    """
    Write records to stdout with proper formatting.
    
    Args:
        headers (list): Column headers
        records (list): List of data rows
        delimiter (str): Field delimiter (',' or '\t')
    """
    writer = csv.writer(sys.stdout, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(headers)
    
    # Clean records to preserve formatting
    for record in records:
        cleaned_record = [clean_cell_for_csv(cell) for cell in record]
        writer.writerow(cleaned_record)


def get_delimiter_for_format(format_name):
    """
    Get appropriate delimiter for output format.
    
    Args:
        format_name (str): 'csv' or 'tsv'
        
    Returns:
        str: Appropriate delimiter
    """
    return '\t' if format_name == 'tsv' else ','

# End of file #
