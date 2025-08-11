"""
aml_voyage_log_parser/voyage_parser_core.py

Core parsing logic using structure-based state machine.
Handles the main parsing workflow and state transitions.
"""

from aml_voyage_log_parser.voyage_models import VoyageCollection, create_voyage
from aml_voyage_log_parser.voyage_patterns import (
    alias_label_rgx,
    arrival_label_rgx,
    barge_label_rgx,
    is_metadata_label,
    is_section_header,
    is_structural_marker,
    port_code_rgx,
    trip_id_rgx,
    tug_label_rgx,
)
from aml_voyage_log_parser.voyage_schedule_parser import parse_ports_and_schedule
from aml_voyage_log_parser.voyage_text_processor import preprocess_text


class VoyageParser:
    """
    Main parser class using structure-based state machine.
    """
    
    def __init__(self, debug=False):
        """
        Initialize parser.
        
        Args:
            debug (bool): Enable debug output
        """
        self.debug = debug
    
    def parse_text(self, text):
        """
        Parse voyage log text and return voyage collection.
        
        Args:
            text (str): Raw text from PDF dump
            
        Returns:
            VoyageCollection: Parsed voyages
        """
        # Preprocess text
        regions_data = preprocess_text(text)
        
        # Parse each region
        collection = VoyageCollection()
        for region_name, region_lines in regions_data.items():
            region_voyages = self._parse_region(region_name, region_lines)
            collection.extend_voyages(region_voyages)
        
        return collection
    
    def _parse_region(self, region_name, lines):
        """
        Parse voyages within a single region.
        
        Args:
            region_name (str): Name of the region
            lines (list): Lines of text in this region
            
        Returns:
            list: List of VoyageData objects
        """
        voyages = []
        current_voyage = None
        state = 'expecting_route_id'
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if state == 'expecting_route_id':
                current_voyage, state = self._handle_route_id(
                    line, region_name, current_voyage, voyages, i
                )
            
            elif state == 'in_metadata':
                state, i = self._handle_metadata(
                    line, current_voyage, lines, i, state
                )
            
            elif state == 'expecting_alias':
                state, i = self._handle_alias(line, current_voyage, i)
            
            elif state == 'expecting_tug':
                state, i = self._handle_tug(line, current_voyage, i)
            
            elif state == 'expecting_barge':
                state, i = self._handle_barge(line, current_voyage, lines, i)
            
            i += 1
        
        # Don't forget the last voyage
        if current_voyage and current_voyage.route:
            voyages.append(current_voyage)
        
        return voyages
    
    def _handle_route_id(self, line, region_name, current_voyage, voyages, line_num):
        """Handle route ID detection."""
        if not is_structural_marker(line):
            # Save previous voyage if exists
            if current_voyage and current_voyage.route:
                voyages.append(current_voyage)
            
            # Start new voyage
            current_voyage = create_voyage(region_name, line)
            
            if self.debug:
                print(f"DEBUG: Found route ID '{line}' at line {line_num} in {region_name}")
            
            return current_voyage, 'in_metadata'
        
        return current_voyage, 'expecting_route_id'
    
    def _handle_metadata(self, line, current_voyage, lines, i, state):
        """Handle metadata section parsing."""
        if alias_label_rgx.match(line):
            return 'expecting_alias', i
        
        elif tug_label_rgx.match(line):
            return 'expecting_tug', i
        
        elif barge_label_rgx.match(line):
            return 'expecting_barge', i
        
        elif trip_id_rgx.match(line):
            current_voyage.trip_id = line
            return 'in_metadata', i
        
        elif arrival_label_rgx.match(line) or port_code_rgx.match(line):
            # Start port/schedule parsing
            ports, new_i = parse_ports_and_schedule(lines, i)
            
            # Add ports to voyage
            for port_data in ports:
                current_voyage.add_port(
                    port_data.get('port', ''),
                    port_data.get('arrival', ''),
                    port_data.get('departure', '')
                )
            
            return 'expecting_route_id', new_i - 1  # -1 because main loop increments
        
        return state, i
    
    def _handle_alias(self, line, current_voyage, i):
        """Handle alias value assignment."""
        if is_metadata_label(line) or is_section_header(line):
            # Hit another label instead of alias data
            current_voyage.alias = ''
            if self.debug:
                print(f"DEBUG: Empty alias for route '{current_voyage.route}' (hit '{line}')")
            return 'in_metadata', i - 1  # Reprocess this line
        else:
            current_voyage.alias = line
            if self.debug:
                print(f"DEBUG: Set alias '{line}' for route '{current_voyage.route}'")
            return 'in_metadata', i
    
    def _handle_tug(self, line, current_voyage, i):
        """Handle tug value assignment."""
        if is_metadata_label(line) or is_section_header(line):
            # Hit another label instead of tug data
            current_voyage.tug = ''
            if self.debug:
                print(f"DEBUG: Empty tug for route '{current_voyage.route}' (hit '{line}')")
            return 'in_metadata', i - 1  # Reprocess this line
        else:
            current_voyage.tug = line
            return 'in_metadata', i
    
    def _handle_barge(self, line, current_voyage, lines, i):
        """Handle barge value assignment."""
        if is_metadata_label(line) or is_section_header(line):
            # Hit another label instead of barge data
            current_voyage.barge = ''
            if self.debug:
                print(f"DEBUG: Empty barge for route '{current_voyage.route}' (hit '{line}')")
            return 'in_metadata', i - 1  # Reprocess this line
        
        elif port_code_rgx.match(line):
            # Hit port codes instead of barge data
            current_voyage.barge = ''
            if self.debug:
                print(f"DEBUG: Empty barge for route '{current_voyage.route}' (hit port '{line}')")
            return 'in_metadata', i - 1  # Reprocess this line
        
        else:
            current_voyage.barge = line
            return 'in_metadata', i

# End of file #
