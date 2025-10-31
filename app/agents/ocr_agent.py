import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

class OcrAgent:
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF, fallback to OCR if needed"""
        tesseract_cmd = os.getenv("TESSERACT_CMD")
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        text = ""
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Try to extract text directly first
            page_text = page.get_text()
            
            # If no text found (scanned PDF), use OCR
            if not page_text.strip():
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                page_text = pytesseract.image_to_string(img, lang=os.getenv("OCR_LANGUAGE", "fra"))
            
            text += page_text + "\n"
        
        doc.close()
        return text
