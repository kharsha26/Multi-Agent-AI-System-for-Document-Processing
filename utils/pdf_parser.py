from PyPDF2 import PdfReader
from io import BytesIO
import logging

logger = logging.getLogger("PDFParser")

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        pdf_file = BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to parse PDF: {str(e)}")
        raise