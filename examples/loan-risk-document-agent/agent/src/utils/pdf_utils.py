"""PDF processing utilities."""

import io
import base64
from typing import List, Optional, Tuple
from PIL import Image
import pypdf
from pdf2image import convert_from_bytes

from src.config import config


def pdf_to_text(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes."""
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        reader = pypdf.PdfReader(pdf_file)
        
        text_parts = []
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        return "\n\n".join(text_parts)
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""


def pdf_to_images(pdf_bytes: bytes, pages: Optional[List[int]] = None, dpi: int = None) -> List[Image.Image]:
    """Convert PDF pages to images.
    
    Args:
        pdf_bytes: PDF file bytes
        pages: Specific pages to convert (1-indexed), None for all
        dpi: DPI for conversion, defaults to config value
    
    Returns:
        List of PIL Image objects
    """
    if dpi is None:
        dpi = config.PDF_DPI
    
    try:
        # Convert PDF to images
        images = convert_from_bytes(
            pdf_bytes,
            dpi=dpi,
            first_page=pages[0] if pages else None,
            last_page=pages[-1] if pages else None
        )
        return images
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []


def pdf_page_to_base64(pdf_bytes: bytes, page_num: int = 1, dpi: int = None) -> Optional[str]:
    """Convert a specific PDF page to base64 encoded image.
    
    Args:
        pdf_bytes: PDF file bytes
        page_num: Page number to convert (1-indexed)
        dpi: DPI for conversion
    
    Returns:
        Base64 encoded image string
    """
    images = pdf_to_images(pdf_bytes, pages=[page_num], dpi=dpi)
    if not images:
        return None
    
    # Convert image to base64
    img_buffer = io.BytesIO()
    images[0].save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    
    return img_base64


def get_pdf_page_count(pdf_bytes: bytes) -> int:
    """Get the number of pages in a PDF."""
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        reader = pypdf.PdfReader(pdf_file)
        return len(reader.pages)
    except Exception as e:
        print(f"Error getting PDF page count: {e}")
        return 0


def extract_pdf_metadata(pdf_bytes: bytes) -> dict:
    """Extract metadata from PDF."""
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        reader = pypdf.PdfReader(pdf_file)
        
        metadata = {}
        if reader.metadata:
            metadata = {
                "title": reader.metadata.get("/Title", ""),
                "author": reader.metadata.get("/Author", ""),
                "subject": reader.metadata.get("/Subject", ""),
                "creator": reader.metadata.get("/Creator", ""),
                "producer": reader.metadata.get("/Producer", ""),
                "creation_date": str(reader.metadata.get("/CreationDate", "")),
                "modification_date": str(reader.metadata.get("/ModDate", ""))
            }
        
        metadata["page_count"] = len(reader.pages)
        return metadata
    except Exception as e:
        print(f"Error extracting PDF metadata: {e}")
        return {}