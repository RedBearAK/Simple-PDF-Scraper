"""
PyPDF processor implementation.
"""

from pathlib import Path
import pypdf

from simple_pdf_scraper.processors.base import PDFProcessor


class PyPDFProcessor(PDFProcessor):
    """
    PDF processor using the pypdf library.
    
    Good balance of speed and reliability for machine-generated PDFs.
    """
    
    def extract_pages(self, pdf_path):
        """Extract text from all pages using pypdf."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        pages_text = []
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                
                for page in reader.pages:
                    # Extract text and clean up common pypdf artifacts
                    text = page.extract_text()
                    # Normalize whitespace but preserve line structure
                    text = self._clean_text(text)
                    pages_text.append(text)
                    
        except Exception as e:
            raise Exception(f"Error reading PDF {pdf_path}: {str(e)}")
        
        return pages_text
    
    def extract_page(self, pdf_path, page_number):
        """Extract text from a specific page using pypdf."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                
                if page_number < 1 or page_number > len(reader.pages):
                    raise IndexError(f"Page {page_number} out of range (1-{len(reader.pages)})")
                
                page = reader.pages[page_number - 1]  # Convert to 0-based
                text = page.extract_text()
                return self._clean_text(text)
                
        except IndexError:
            raise
        except Exception as e:
            raise Exception(f"Error reading page {page_number} from PDF {pdf_path}: {str(e)}")
    
    def get_page_count(self, pdf_path):
        """Get page count efficiently using pypdf."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                return len(reader.pages)
        except Exception as e:
            raise Exception(f"Error reading PDF {pdf_path}: {str(e)}")
    
    def _clean_text(self, text):
        """
        Clean up text extracted by pypdf.
        
        Remove common artifacts while preserving the structure needed
        for pattern matching.
        """
        if not text:
            return ""
        
        # Replace multiple consecutive spaces with single space
        # but preserve line breaks for positional matching
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Normalize spaces within lines
            cleaned_line = ' '.join(line.split())
            if cleaned_line:  # Only keep non-empty lines
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def get_processor_info(self):
        """Return information about this processor."""
        return {
            'name': 'PyPDF',
            'library': 'pypdf',
            'version': getattr(pypdf, '__version__', 'unknown'),
            'features': ['text_extraction', 'page_count', 'fast_processing'],
            'best_for': 'machine_generated_pdfs'
        }
