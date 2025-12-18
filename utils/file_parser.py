import pdfplumber
from PIL import Image
import pytesseract
import io

def extract_text_from_file(uploaded_file):
    text = ""

    file_type = uploaded_file.type

    try:
        # PDF
        if file_type == "application/pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""

        # Image
        elif file_type in ["image/png", "image/jpeg", "image/jpg"]:
            image = Image.open(uploaded_file)
            text = pytesseract.image_to_string(image)

    except Exception as e:
        print("Extraction error:", e)

    return text.strip()
