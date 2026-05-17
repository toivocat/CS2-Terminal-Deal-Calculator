from pytesseract import pytesseract
from PIL import Image
import enum

# THE TEXT RECOGNITION
class OS(enum.Enum):
    Windows = 1

class Language(enum.Enum):
    ENG = "eng"
    RUS = "rus"
    ITA = "ita"

class ImageReader:
    def __init__(self, os: OS):
        if os == OS.Windows:
            windows_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            pytesseract.tesseract_cmd = windows_path
            print("Working on Windows\n")

    def extract_text(self, image: str, lang: str) -> str:
        img = Image.open(image)
        extracted_text = pytesseract.image_to_string(img, lang=lang)
        return extracted_text