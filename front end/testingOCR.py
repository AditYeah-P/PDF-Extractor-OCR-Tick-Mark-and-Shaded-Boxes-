import requests

def upload_pdf_and_get_ocr(pdf_path, server_url):
    # Define the endpoint URL
    upload_url = f"{server_url}/upload/"
    
    # Open the PDF file in binary mode
    with open(pdf_path, 'rb') as pdf_file:
        # Create a dictionary with the file to upload
        files = {'file': pdf_file}
        
        # Send the POST request to the server
        response = requests.post(upload_url, files=files)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            ocr_result = response.json()
            return ocr_result
        else:
            # Handle the error
            print(f"Failed to upload PDF. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None

# Define the path to the PDF file and the server URL
pdf_path = 'aiwplain1.pdf'
server_url = 'https://1c7c-35-247-131-217.ngrok-free.app'  # Replace with your ngrok URL

# Call the function to upload the PDF and get the OCR result
ocr_result = upload_pdf_and_get_ocr(pdf_path, server_url)

def ocr_result_to_string(ocr_result):
    # Extract the list of text items from the OCR result
    text_items = ocr_result['ocr_results']['pdf_images/page_1.png']
    
    # Sort the items by their position in the original document
    # This assumes that the items are roughly in the correct order
    sorted_items = sorted(text_items, key=lambda x: x['confidence'], reverse=True)
    
    # Extract just the text from each item
    text_only = [item['text'] for item in text_items]
    
    # Join the text items into a single string
    result_string = ' '.join(text_only)
    
    return result_string
# Print the OCR result
if ocr_result:
    print("OCR Result:")
    # print(ocr_results_to_string(ocr_result))
    print(ocr_result)
    print(ocr_result_to_string(ocr_result))

