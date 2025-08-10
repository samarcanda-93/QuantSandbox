#!/usr/bin/env python3

import requests
import os
import json

def test_hf_error_cases():
    """Test Hugging Face API error handling scenarios."""
    
    print("Testing Hugging Face API Error Cases")
    print("="*40)
    
    # Test 1: Invalid API token
    print("\n1. Testing with invalid API token...")
    test_invalid_token()
    
    # Test 2: No API token (public access)
    print("\n2. Testing without API token...")
    test_no_token()
    
    # Test 3: Network timeout
    print("\n3. Testing timeout handling...")
    test_timeout()
    
    # Test 4: Invalid model endpoint
    print("\n4. Testing invalid model endpoint...")
    test_invalid_endpoint()
    
    # Test 5: Malformed payload
    print("\n5. Testing malformed payload...")
    test_malformed_payload()

def test_invalid_token():
    """Test with invalid API token."""
    api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": "Bearer invalid_token_123"}
    
    payload = {
        "inputs": {
            "source_sentence": "APL",
            "sentences": ["AAPL", "MSFT"]
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  Exception: {e}")

def test_no_token():
    """Test without API token (public access)."""
    api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    
    payload = {
        "inputs": {
            "source_sentence": "APL",
            "sentences": ["AAPL", "MSFT"]
        }
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Success: {response.json()}")
        else:
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  Exception: {e}")

def test_timeout():
    """Test timeout handling."""
    api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    
    payload = {
        "inputs": {
            "source_sentence": "APL",
            "sentences": ["AAPL", "MSFT"]
        }
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=0.001)  # Very short timeout
        print(f"  Unexpected success: {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"  Timeout handled correctly")
    except Exception as e:
        print(f"  Other exception: {e}")

def test_invalid_endpoint():
    """Test invalid model endpoint."""
    api_url = "https://api-inference.huggingface.co/models/nonexistent/model"
    
    payload = {
        "inputs": {
            "source_sentence": "APL",
            "sentences": ["AAPL", "MSFT"]
        }
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=10)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  Exception: {e}")

def test_malformed_payload():
    """Test malformed payload."""
    api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    
    # Invalid payload structure
    payload = {
        "wrong_field": "invalid"
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=10)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  Exception: {e}")

def test_integrated_error_handling():
    """Test the integrated utils.py error handling."""
    print("\n6. Testing integrated error handling...")
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from ai_utils import try_huggingface_suggestions
        
        # Save original token
        original_token = os.environ.get('HF_API_TOKEN', '')
        
        # Test with invalid token
        os.environ['HF_API_TOKEN'] = 'invalid_token'
        result = try_huggingface_suggestions('APL')
        print(f"  Invalid token result: {result}")
        
        # Restore original token
        if original_token:
            os.environ['HF_API_TOKEN'] = original_token
        else:
            os.environ.pop('HF_API_TOKEN', None)
            
    except Exception as e:
        print(f"  Exception in integrated test: {e}")

if __name__ == "__main__":
    test_hf_error_cases()
    test_integrated_error_handling()