#!/usr/bin/env python3
"""Debug email chat endpoint."""

import requests
import json

# Test the email chat endpoint
url = "http://localhost:8000/emails/chat"
data = {
    "message": "Show me emails about maritime safety",
    "context_emails": 5,
    "include_metadata": True
}

print("Testing email chat endpoint...")
print(f"URL: {url}")
print(f"Request data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    # Try to get response content
    if response.content:
        try:
            json_response = response.json()
            print(f"\nJSON Response: {json.dumps(json_response, indent=2)}")
        except:
            print(f"\nRaw Response: {response.text}")
    else:
        print("\nNo response content")
        
except Exception as e:
    print(f"\nError: {e}")
