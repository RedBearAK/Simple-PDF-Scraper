"""
aml_voyage_log_parser/voyage_text_processor.py

Text preprocessing functions for voyage log parsing.
Handles pollution filtering and region splitting.
"""

from aml_voyage_log_parser.voyage_patterns import known_regions, pollution_patterns


def filter_pollution(text):
    """
    Remove PDF header pollution and return clean lines.
    
    Args:
        text (str): Raw text from PDF dump
        
    Returns:
        list: List of clean text lines
    """
    all_lines = [line.strip() for line in text.split('\n') if line.strip()]
    clean_lines = []
    
    for line in all_lines:
        if not _is_pollution_line(line):
            clean_lines.append(line)
    
    return clean_lines


def _is_pollution_line(line):
    """
    Check if a line matches any pollution pattern.
    
    Args:
        line (str): Text line to check
        
    Returns:
        bool: True if line is pollution
    """
    for pattern in pollution_patterns:
        if pattern.search(line):
            return True
    return False


def split_by_regions(lines):
    """
    Split lines into regions, handling repeated region headers.
    
    Args:
        lines (list): List of clean text lines
        
    Returns:
        dict: Region name -> list of lines in that region
    """
    regions = {}
    current_region = None
    current_lines = []
    
    for line in lines:
        if line in known_regions:
            # Save previous region
            if current_region and current_lines:
                _add_region_lines(regions, current_region, current_lines)
            
            # Start new region
            current_region = line
            current_lines = []
        else:
            if current_region:  # Only collect if we're in a region
                current_lines.append(line)
    
    # Don't forget the last region
    if current_region and current_lines:
        _add_region_lines(regions, current_region, current_lines)
    
    return regions


def _add_region_lines(regions, region_name, lines):
    """
    Add lines to a region, appending if region already exists.
    
    Args:
        regions (dict): Current regions dictionary
        region_name (str): Name of the region
        lines (list): Lines to add to the region
    """
    if region_name in regions:
        regions[region_name].extend(lines)
    else:
        regions[region_name] = lines


def preprocess_text(text):
    """
    Complete text preprocessing pipeline.
    
    Args:
        text (str): Raw text from PDF dump
        
    Returns:
        dict: Region name -> list of clean lines
    """
    clean_lines = filter_pollution(text)
    return split_by_regions(clean_lines)


def get_preprocessing_stats(text, regions_data):
    """
    Get statistics about text preprocessing.
    
    Args:
        text (str): Original raw text
        regions_data (dict): Processed regions data
        
    Returns:
        dict: Statistics about preprocessing
    """
    original_lines = len([line for line in text.split('\n') if line.strip()])
    clean_lines = sum(len(lines) for lines in regions_data.values())
    filtered_lines = original_lines - clean_lines
    
    return {
        'original_lines': original_lines,
        'clean_lines': clean_lines,
        'filtered_lines': filtered_lines,
        'regions_found': len(regions_data),
        'region_names': list(regions_data.keys())
    }

# End of file #
