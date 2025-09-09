"""Document processing tools for the workflow."""

import base64
import io
from typing import Optional, Dict, Any, List
from PIL import Image
import pypdf
from pdf2image import convert_from_bytes
import pandas as pd


def pdf_to_image_base64(pdf_bytes: bytes, page_num: int = 1, dpi: int = 150) -> Optional[str]:
    """Convert a PDF page to base64 encoded image."""
    try:
        images = convert_from_bytes(pdf_bytes, dpi=dpi, first_page=page_num, last_page=page_num)
        if images:
            img_buffer = io.BytesIO()
            images[0].save(img_buffer, format='PNG')
            img_buffer.seek(0)
            return base64.b64encode(img_buffer.read()).decode('utf-8')
    except Exception as e:
        print(f"Error converting PDF to image: {e}")
    return None


def pdf_to_all_images_base64(pdf_bytes: bytes, dpi: int = 150) -> List[str]:
    """Convert ALL PDF pages to base64 encoded images."""
    try:
        # Convert all pages at once
        images = convert_from_bytes(pdf_bytes, dpi=dpi)
        base64_images = []
        
        for i, image in enumerate(images):
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            base64_str = base64.b64encode(img_buffer.read()).decode('utf-8')
            base64_images.append(base64_str)
            print(f"  Converted PDF page {i+1} to image")
        
        return base64_images
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []


def pdf_to_text(pdf_bytes: bytes) -> str:
    """Extract all text from a PDF."""
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        reader = pypdf.PdfReader(pdf_file)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n\n".join(text_parts)
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""


def image_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64."""
    return base64.b64encode(image_bytes).decode('utf-8')


def csv_to_text_preview(csv_bytes: bytes, max_rows: int = 100) -> str:
    """Convert CSV to text preview for analysis."""
    try:
        csv_content = csv_bytes.decode('utf-8')
    except:
        csv_content = csv_bytes.decode('latin-1')
    
    try:
        df = pd.read_csv(io.StringIO(csv_content))
        
        # Create a text summary
        summary = f"CSV with {len(df)} rows and columns: {', '.join(df.columns)}\n\n"
        
        # Add first N rows as preview
        if len(df) > 0:
            preview_df = df.head(max_rows)
            summary += "Data preview:\n"
            summary += preview_df.to_string(index=False)
        
        return summary
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return csv_content[:5000]  # Return raw text if parsing fails


def prepare_document_for_ai(file_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare a document for AI processing."""
    file_type = file_data["type"].lower()
    file_content = file_data["content"]
    
    result = {
        "type": file_type,
        "name": file_data.get("name", "document"),
        "content_type": None,
        "content": None
    }
    
    if file_type == "pdf":
        # Convert ALL pages to images for complete extraction
        all_images_b64 = pdf_to_all_images_base64(file_content)
        
        if all_images_b64:
            result["content_type"] = "images"  # Multiple images
            result["content"] = all_images_b64  # List of base64 images
            print(f"  Prepared {len(all_images_b64)} page(s) from PDF")
        else:
            # Fallback to text extraction if image conversion fails
            text_content = pdf_to_text(file_content)
            result["content_type"] = "text"
            result["content"] = text_content
            print(f"  Fallback to text extraction")
            
    elif file_type in ["png", "jpg", "jpeg"]:
        result["content_type"] = "images"  # Always use "images" for consistency
        result["content"] = [image_to_base64(file_content)]  # Always return list
        
    elif file_type == "csv":
        result["content_type"] = "text"
        result["content"] = csv_to_text_preview(file_content)
    
    return result