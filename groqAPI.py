import os

from groq import Groq

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



client = Groq(
    api_key="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",
)

chat_completion = client.chat.completions.create(
    messages=[ 
        {
            "role": "system",
            "content": "For the prompt outputs. Don't add any unnecessary messages including final note. Just display the output",
        },
        {
            "role": "user",
            "content": f"{ocr_pdf_text} Don't include any messages from the model such as 'Here is the extracted data.....'Clean and Extract the above output and put them in single csv file. Don't include sub-headings like: Personal Information, Professional Details, Practice Information, Claims History, Additional Risk Factors. Include the header rows and the subsequent rows continuously with a comma.",
        },
        {
            "role": "user",
            "content": "Include the header rows and the subsequent rows continuously with a comma.",
        },
        {
            "role": "system",
            "content": "Please extract the relevant information from the text and format it into a single CSV file.",
        }
    ],
    model="llama3-8b-8192",
)


csv = chat_completion.choices[0].message.content.replace('"', '').replace("'", '').replace("_", " ")
#print(chat_completion.choices[0].message.content)
#print(csv)