"""
aml_voyage_log_parser/voyage_schedule_parser.py

Port and schedule parsing functions.
Handles extraction of port codes and arrival/departure times.
"""

from aml_voyage_log_parser.voyage_patterns import (
    arrival_label_rgx,
    date_rgx,
    departure_label_rgx,
    is_structural_marker,
    port_code_rgx,
    time_rgx,
)


def parse_ports_and_schedule(lines, start_idx):
    """
    Parse ports and their arrival/departure schedule.
    
    Args:
        lines (list): List of text lines
        start_idx (int): Starting index for parsing
        
    Returns:
        tuple: (ports_list, new_index)
    """
    port_codes = collect_port_codes(lines, start_idx)
    arrival_times, arrival_end_idx = collect_arrival_times(lines, start_idx)
    departure_times, departure_end_idx = collect_departure_times(lines, arrival_end_idx)
    
    ports = build_port_schedule(port_codes, arrival_times, departure_times)
    
    return ports, departure_end_idx


def collect_port_codes(lines, start_idx):
    """
    Collect all port codes until we hit "Arrival" or structural marker.
    
    Args:
        lines (list): List of text lines
        start_idx (int): Starting index
        
    Returns:
        list: List of port codes
    """
    port_codes = []
    i = start_idx
    
    while i < len(lines):
        line = lines[i].strip()
        
        if arrival_label_rgx.match(line) or is_structural_marker(line):
            break
        
        # Collect port codes (only exact 3-letter matches)
        if port_code_rgx.match(line):
            port_codes.append(line)
        
        i += 1
    
    return port_codes


def collect_arrival_times(lines, start_idx):
    """
    Find and collect arrival dates and times.
    
    Args:
        lines (list): List of text lines
        start_idx (int): Starting index
        
    Returns:
        tuple: (arrival_times_list, end_index)
    """
    # Find "Arrival" section
    i = start_idx
    while i < len(lines) and not arrival_label_rgx.match(lines[i].strip()):
        i += 1
    
    if i >= len(lines):
        return [], i
    
    i += 1  # Skip "Arrival" line
    
    # Collect dates and times
    dates, times, end_idx = collect_date_time_pairs(lines, i, departure_label_rgx)
    
    # Combine into formatted strings
    arrival_times = combine_dates_and_times(dates, times)
    
    return arrival_times, end_idx


def collect_departure_times(lines, start_idx):
    """
    Find and collect departure dates and times.
    
    Args:
        lines (list): List of text lines
        start_idx (int): Starting index
        
    Returns:
        tuple: (departure_times_list, end_index)
    """
    # Find "Departure" section
    i = start_idx
    while i < len(lines) and not departure_label_rgx.match(lines[i].strip()):
        i += 1
    
    if i >= len(lines):
        return [], i
    
    i += 1  # Skip "Departure" line
    
    # Collect dates and times until pattern breaks
    dates, times, end_idx = collect_date_time_pairs(lines, i, None)
    
    # Combine into formatted strings
    departure_times = combine_dates_and_times(dates, times)
    
    return departure_times, end_idx


def collect_date_time_pairs(lines, start_idx, stop_pattern):
    """
    Collect date and time lines until pattern breaks or stop pattern found.
    
    Args:
        lines (list): List of text lines
        start_idx (int): Starting index
        stop_pattern: Regex pattern to stop at (or None)
        
    Returns:
        tuple: (dates_list, times_list, end_index)
    """
    dates = []
    times = []
    i = start_idx
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for stop pattern
        if stop_pattern and stop_pattern.match(line):
            break
        
        # Collect dates and times
        if date_rgx.match(line):
            dates.append(line)
        elif time_rgx.match(line):
            times.append(line)
        else:
            # Hit something that's not date/time, we're done
            break
        
        i += 1
    
    return dates, times, i


def combine_dates_and_times(dates, times):
    """
    Combine parallel date and time lists into formatted strings.
    
    Args:
        dates (list): List of date strings
        times (list): List of time strings
        
    Returns:
        list: List of "MM/DD/YYYY HH:MM:SS" strings
    """
    combined = []
    for j in range(min(len(dates), len(times))):
        combined.append(f"{dates[j]} {times[j]}")
    return combined


def build_port_schedule(port_codes, arrival_times, departure_times):
    """
    Build port schedule using sawtooth pattern.
    
    Args:
        port_codes (list): List of port codes
        arrival_times (list): List of arrival times
        departure_times (list): List of departure times
        
    Returns:
        list: List of port data dictionaries
    """
    ports = []
    
    for i_port, port_code in enumerate(port_codes):
        port_data = {'port': port_code}
        
        # Arrival: use arrival[i-1] if not first port
        if i_port == 0:
            port_data['arrival'] = ''
        else:
            if i_port - 1 < len(arrival_times):
                port_data['arrival'] = arrival_times[i_port - 1]
            else:
                port_data['arrival'] = ''
        
        # Departure: use departure[i] if not last port
        if i_port == len(port_codes) - 1:
            port_data['departure'] = ''
        else:
            if i_port < len(departure_times):
                port_data['departure'] = departure_times[i_port]
            else:
                port_data['departure'] = ''
        
        ports.append(port_data)
    
    return ports

# End of file #
