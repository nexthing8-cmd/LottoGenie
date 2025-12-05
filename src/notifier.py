import requests
import json
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()

# The incoming webhook URL provided in instructions
# Note: The token in the instruction contains %22 (double quote) at start and end.
# We will use the URL exactly as provided, but usually it's better to verify if quotes are part of the token.
# Assuming %22 is part of the token or just URL encoded quotes.
# We will construct the request carefully.

WEBHOOK_URL = os.getenv('WEBHOOK_URL')

def send_message(text):
    """
    Sends a message to Synology Chat via Incoming Webhook.
    
    Args:
        text (str): The message content to send.
    """
    payload = {"text": text}
    
    try:
        # Synology Chat expects payload as a form parameter 'payload' which is a JSON string
        # properly encoded? or just as data?
        # Standard Synology Chat incoming webhook documentation says:
        # POST request with 'payload' parameter containing JSON string.
        
        data = {'payload': json.dumps(payload)}
        
        response = requests.post(WEBHOOK_URL, data=data)
        
        if response.status_code == 200:
            print(f"Notification sent successfully: {text}")
        else:
            print(f"Failed to send notification. Status: {response.status_code}, Response: {response.text}")
            
    except Exception as e:
        print(f"Error sending notification: {e}")

if __name__ == "__main__":
    # Test
    send_message("LottoGenie Notification System Test")
