"""
aml_voyage_log_parser/voyage_models.py

Data structures and models for voyage log parsing.
Handles voyage data representation and conversion to output formats.
"""


class VoyageData:
    """
    Represents a single voyage with all associated metadata and ports.
    """
    
    def __init__(self, region, route):
        """
        Initialize a new voyage.
        
        Args:
            region (str): Region name (Central, Charter, etc.)
            route (str): Route identifier
        """
        self.region = region
        self.route = route
        self.trip_id = ''
        self.alias = ''
        self.tug = ''
        self.barge = ''
        self.ports = []
    
    def add_port(self, port_code, arrival='', departure=''):
        """
        Add a port to this voyage.
        
        Args:
            port_code (str): 3-letter port code
            arrival (str): Arrival date/time
            departure (str): Departure date/time
        """
        port_data = {
            'port': port_code,
            'arrival': arrival,
            'departure': departure
        }
        self.ports.append(port_data)
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'region': self.region,
            'route': self.route,
            'trip_id': self.trip_id,
            'alias': self.alias,
            'tug': self.tug,
            'barge': self.barge,
            'ports': self.ports
        }
    
    def has_ports(self):
        """Check if voyage has any ports."""
        return len(self.ports) > 0
    
    def port_count(self):
        """Get number of ports in this voyage."""
        return len(self.ports)


class VoyageCollection:
    """
    Collection of voyages with conversion capabilities.
    """
    
    def __init__(self):
        """Initialize empty voyage collection."""
        self.voyages = []
    
    def add_voyage(self, voyage):
        """
        Add a voyage to the collection.
        
        Args:
            voyage (VoyageData): Voyage to add
        """
        self.voyages.append(voyage)
    
    def extend_voyages(self, voyages):
        """
        Add multiple voyages to the collection.
        
        Args:
            voyages (list): List of VoyageData objects
        """
        self.voyages.extend(voyages)
    
    def to_flat_records(self):
        """
        Convert all voyages to flat records for CSV output.
        
        Returns:
            list: List of records, each record is a list of values
        """
        records = []
        
        for voyage in self.voyages:
            base_record = [
                voyage.region,
                voyage.route,
                voyage.trip_id,
                voyage.alias,
                voyage.tug,
                voyage.barge
            ]
            
            # Create one record per port
            for port_data in voyage.ports:
                record = base_record + [
                    port_data.get('port', ''),
                    port_data.get('arrival', ''),
                    port_data.get('departure', '')
                ]
                records.append(record)
        
        return records
    
    def get_headers(self):
        """
        Get column headers for CSV output.
        
        Returns:
            list: Column headers
        """
        return [
            'Region', 'Route', 'Trip_ID', 'Alias', 
            'Tug', 'Barge', 'Port', 'Arrival', 'Departure'
        ]
    
    def voyage_count(self):
        """Get total number of voyages."""
        return len(self.voyages)
    
    def total_ports(self):
        """Get total number of port records across all voyages."""
        return sum(voyage.port_count() for voyage in self.voyages)
    
    def group_by_region(self):
        """
        Group voyages by region.
        
        Returns:
            dict: Region name -> list of voyages
        """
        by_region = {}
        for voyage in self.voyages:
            region = voyage.region
            if region not in by_region:
                by_region[region] = []
            by_region[region].append(voyage)
        return by_region


def create_voyage(region, route):
    """
    Factory function to create a new voyage.
    
    Args:
        region (str): Region name
        route (str): Route identifier
        
    Returns:
        VoyageData: New voyage instance
    """
    return VoyageData(region, route)

# End of file #
