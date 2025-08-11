"""
aml_voyage_log_parser/__init__.py

A modular parser for AML voyage log text dumps.
Extracts structured data from PDF text dumps using document structure.
"""

__version__ = "1.0.0"
__author__ = "AML Voyage Parser Team"

from aml_voyage_log_parser.voyage_parser_core import VoyageParser
from aml_voyage_log_parser.voyage_models import VoyageCollection, VoyageData

__all__ = ['VoyageParser', 'VoyageCollection', 'VoyageData']

# End of file #
