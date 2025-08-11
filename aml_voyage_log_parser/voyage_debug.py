"""
aml_voyage_log_parser/voyage_debug.py

Debug and diagnostic utilities for voyage parsing.
Provides insight into parsing process and data structures.
"""

from aml_voyage_log_parser.voyage_patterns import (
    is_metadata_label,
    is_section_header,
    port_code_rgx,
    trip_id_rgx,
)
from aml_voyage_log_parser.voyage_text_processor import preprocess_text


def show_structural_debug(text):
    """
    Show detailed structural parsing debug information.
    
    Args:
        text (str): Raw text from PDF dump
    """
    regions_data = preprocess_text(text)
    
    print("=== STRUCTURAL PARSING DEBUG ===")
    for region_name, region_lines in regions_data.items():
        show_region_structure(region_name, region_lines)


def show_region_structure(region_name, region_lines, max_lines=20):
    """
    Show structure of a single region.
    
    Args:
        region_name (str): Name of the region
        region_lines (list): Lines in this region
        max_lines (int): Maximum lines to show
    """
    print(f"\n{region_name} Region ({len(region_lines)} lines):")
    
    # Show structural markers and patterns
    for i, line in enumerate(region_lines[:max_lines]):
        markers = analyze_line_structure(line)
        marker_str = f" <- {', '.join(markers)}" if markers else ""
        print(f"    {i+1:2}: {line}{marker_str}")
    
    if len(region_lines) > max_lines:
        print(f"    ... and {len(region_lines) - max_lines} more lines")


def analyze_line_structure(line):
    """
    Analyze what structural elements a line contains.
    
    Args:
        line (str): Text line to analyze
        
    Returns:
        list: List of structural markers found
    """
    markers = []
    
    if is_metadata_label(line):
        markers.append("METADATA_LABEL")
    if is_section_header(line):
        markers.append("SECTION_HEADER")
    if trip_id_rgx.match(line):
        markers.append("TRIP_ID")
    if port_code_rgx.match(line):
        markers.append("PORT")
    
    return markers


def show_voyage_summary(collection):
    """
    Show summary of parsed voyages.
    
    Args:
        collection (VoyageCollection): Parsed voyage collection
    """
    print(f"Parsed {collection.voyage_count()} total voyages:")
    
    # Show first few voyages
    for voyage in collection.voyages[:5]:
        alias_info = f" (Alias: '{voyage.alias}')" if voyage.alias else ""
        print(f"  {voyage.region:10} {voyage.route:6} {voyage.port_count()} ports{alias_info}")
    
    if collection.voyage_count() > 5:
        print(f"  ... and {collection.voyage_count() - 5} more voyages")
    
    print("")


def show_preview(collection):
    """
    Show preview of parsed data grouped by region.
    
    Args:
        collection (VoyageCollection): Parsed voyage collection
    """
    print(f"Found {collection.voyage_count()} voyages:")
    
    # Group by region for summary
    by_region = collection.group_by_region()
    
    for region, region_voyages in by_region.items():
        print(f"\n{region} ({len(region_voyages)} voyages):")
        for voyage in region_voyages[:3]:  # Show first 3 per region
            alias_info = f" (Alias: {voyage.alias})" if voyage.alias else ""
            print(f"  {voyage.route}: {voyage.port_count()} ports{alias_info}")
        if len(region_voyages) > 3:
            print(f"  ... and {len(region_voyages) - 3} more voyages")


def show_sample_records(collection, max_records=5):
    """
    Show sample CSV records.
    
    Args:
        collection (VoyageCollection): Parsed voyage collection
        max_records (int): Maximum records to show
    """
    headers = collection.get_headers()
    records = collection.to_flat_records()
    
    print(f"\nSample records (first {max_records} of {len(records)}):")
    print('\t'.join(headers))
    
    for record in records[:max_records]:
        print('\t'.join(str(cell) for cell in record))
    
    if len(records) > max_records:
        print(f"... and {len(records) - max_records} more records")


def get_parsing_stats(collection):
    """
    Get detailed statistics about parsing results.
    
    Args:
        collection (VoyageCollection): Parsed voyage collection
        
    Returns:
        dict: Parsing statistics
    """
    by_region = collection.group_by_region()
    
    stats = {
        'total_voyages': collection.voyage_count(),
        'total_ports': collection.total_ports(),
        'regions': len(by_region),
        'region_breakdown': {}
    }
    
    for region, voyages in by_region.items():
        stats['region_breakdown'][region] = {
            'voyages': len(voyages),
            'ports': sum(v.port_count() for v in voyages)
        }
    
    return stats

# End of file #
