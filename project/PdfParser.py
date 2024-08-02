import google.generativeai as genai
import os
import pytesseract
from pdf2image import convert_from_path

def ocr_extract_text_from_pdf(file_path):
    text = ""
    # Convert PDF to images
    pages = convert_from_path(file_path)
    # Perform OCR on each page
    for page in pages:
        text += pytesseract.image_to_string(page)
    print(text)
    return text


def extract_csv_from_pdf(file_path):
    ocr_pdf_text = ocr_extract_text_from_pdf(file_path)
    
    genai.configure(api_key='AIzaSyBGZNshO8QDWjX9K9FIqxnIhuEvW_OjZK8')

    model = genai.GenerativeModel('gemini-1.5-flash')

    response = model.generate_content(f"Analyse the text given and return ONLY a csv. Prefix the headers of all multiple choice columns with RADIO_ but do not add this prefix to the values. Clean and Extract the above output and put them in a single CSV file. Include the header rows and the subsequent rows continuously with a comma. \n{ocr_pdf_text}")
    #response = model.generate_content(f"Analyse the text given and return ONLY a csv. All Multiple choice columns must have the RADIO_ prefix.\n\n{ocr_pdf_text} Clean and Extract the above output and put them in a single CSV file. Include the header rows and the subsequent rows continuously with a comma.")

    csv = response.text
    
    print(csv)
    return csv

# file_path = 'elonMusk.pdf'
# csv = extract_csv_from_pdf(file_path)
# print(csv)
