"""
aml_voyage_log_parser/voyage_patterns.py

Structural patterns for voyage log parsing - focused on labels and document markers,
not content validation. This approach works with document structure instead of 
fighting fragile content patterns.
"""

import re


# Document structure markers (exact label matches)
alias_label_rgx = re.compile(r'^Alias:$')
tug_label_rgx = re.compile(r'^Tug:$')
barge_label_rgx = re.compile(r'^Barge:$')
arrival_label_rgx = re.compile(r'^Arrival$')
departure_label_rgx = re.compile(r'^Departure$')

# Port codes (3-letter airport/port codes) - must be exact match on whole line
port_code_rgx = re.compile(r'^[A-Z]{3}$')

# Date and time patterns
date_rgx = re.compile(r'\d{2}/\d{2}/\d{4}')
time_rgx = re.compile(r'\d{2}:\d{2}:\d{2}')
datetime_combined_rgx = re.compile(r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$')

# Trip ID pattern (pure numeric lines)
trip_id_rgx = re.compile(r'^\d+$')

# Known regions (for initial document splitting)
known_regions = ['Central', 'Charter', 'Hawaii', 'Southeast', 'Western']

# PDF header pollution patterns (for filtering)
pollution_patterns = [
    re.compile(r'Gray = "Completed"'),
    re.compile(r'Green = "Upcoming"'),
    re.compile(r'Report Date/Time:'),
    re.compile(r'Voyage Log: All Regions'),
    re.compile(r'This site provides estimate'),
    re.compile(r'shipments\. Shipment availability'),
    re.compile(r'Lynden Tracking Center'),
    re.compile(r'TEXT DUMP:'),
    re.compile(r'Total pages:'),
    re.compile(r'Extracted:'),
    re.compile(r'--- PAGE \d+ ---'),
    re.compile(r'Region/Route'),
    re.compile(r'Trip'),
    re.compile(r'Tug/Barge/Notes'),
    re.compile(r'^=+$')  # Lines of equal signs
]

# Helper functions
def is_metadata_label(line):
    """Check if line is a metadata label (Alias:, Tug:, Barge:)."""
    return (alias_label_rgx.match(line) or 
            tug_label_rgx.match(line) or 
            barge_label_rgx.match(line))

def is_section_header(line):
    """Check if line is a section header (Arrival, Departure)."""
    return (arrival_label_rgx.match(line) or 
            departure_label_rgx.match(line))

def is_structural_marker(line):
    """Check if line is any kind of structural marker."""
    return (is_metadata_label(line) or 
            is_section_header(line))

# End of file #
