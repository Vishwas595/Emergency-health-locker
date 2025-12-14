import pdfplumber
import pytesseract
from PIL import Image
import io

def extract_text_from_file(uploaded_file):
    """
    Extract text from PDF or Image file
    """
    file_type = uploaded_file.type

    # PDF
    if file_type == "application/pdf":
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()

    # Image
    elif file_type in ["image/png", "image/jpeg", "image/jpg"]:
        image = Image.open(uploaded_file)
        text = pytesseract.image_to_string(image)
        return text.strip()

    else:
        return "Unsupported file format"
