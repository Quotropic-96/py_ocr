import json
import requests
from google.oauth2 import service_account
from google.auth.transport import requests as grequests
import base64
import os

# Constants
ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
CREDENTIALS_PATH = './nadal-ocr-auth.json'
OUTPUT_DIR = 'output'

def get_access_token(credentials_path):
    """Get access token from service account credentials."""
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    
    request = grequests.Request()  # Using the Request class from google.auth.transport.requests
    credentials.refresh(request)   # Refresh the credentials with the request object

    return credentials.token

def annotate_image(image_path, access_token):
    """Send image to Google Cloud Vision API for annotation."""
    
    # Load image and encode in base64
    with open(image_path, 'rb') as f:
        image_data = f.read()
        encoded_image_data = base64.b64encode(image_data).decode('utf-8')

    # Construct request payload
    payload = {
        "requests": [
            {
                "image": {
                    "content": encoded_image_data
                },
                "features": [
                    {
                        "type": "TEXT_DETECTION",
                        "maxResults": 5
                    }
                ]
            }
        ]
    }

    # Set headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Make POST request
    response = requests.post(ENDPOINT_URL, headers=headers, data=json.dumps(payload))
    response_data = response.json()

    # Save for parsing
    save_to_json(response_data, 'response_data.json')
    
    # Check for errors
    if 'error' in response_data['responses'][0]:
        raise Exception(response_data['responses'][0]['error']['message'])

    # Extract text annotations
    text_annotations = response_data['responses'][0].get('textAnnotations', [])
    if not text_annotations:
        raise Exception("No text annotations found in the image.")
    return text_annotations

def save_to_json(data, filename):
    # Ensure the output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # Join the path with the output directory
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_from_json(filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'r') as f:
        return json.load(f)


# Main execution
if __name__ == "__main__":
    access_token = get_access_token(CREDENTIALS_PATH)
    annotations = annotate_image('./images/test.png', access_token)
    
    for annotation in annotations:
        print(annotation['description'])

