import pytesseract
from pdf2image import convert_from_path

# Function to perform OCR on the PDF and extract text
def ocr_extract_text_from_pdf(file_path):
    text = ""
    # Convert PDF to images
    pages = convert_from_path(file_path)
    # Perform OCR on each page
    for page in pages:
        text += pytesseract.image_to_string(page)
    return text

# Replace 'your_pdf_file.pdf' with the path to your PDF file
file_path = 'elonMusk.pdf'
ocr_pdf_text = ocr_extract_text_from_pdf(file_path)
print(ocr_pdf_text)

