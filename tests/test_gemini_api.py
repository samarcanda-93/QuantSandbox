#!/usr/bin/env python3
"""
Debug script to test the Gemini API call directly
"""
import os
import requests
import json

def test_gemini_api():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("No API key found!")
        return
    
    print(f"API Key starts with: {api_key[:10]}...")
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }
    
    data = {
        "contents": [{
            "parts": [{"text": "Hello, just respond with 'TEST SUCCESS'"}]
        }]
    }
    
    try:
        print("Making API request...")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"AI Response: {text}")
            else:
                print("No candidates in response")
        else:
            print("API call failed")
            
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_api()