import json
import requests
from google.oauth2 import service_account

# Constants
ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
CREDENTIALS_PATH = 'path_to_your_service_account_key.json'

def get_access_token(credentials_path):
    """Get access token from service account credentials."""
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
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

    # Check for errors
    if 'error' in response_data:
        raise Exception(response_data['error'])

    # Extract text annotations
    text_annotations = response_data['responses'][0]['textAnnotations']
    return text_annotations

# Main execution
if __name__ == "__main__":
    access_token = get_access_token(CREDENTIALS_PATH)
    annotations = annotate_image('path_to_your_image.png', access_token)
    
    for annotation in annotations:
        print(annotation['description'])

