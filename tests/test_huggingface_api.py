#!/usr/bin/env python3

import requests
import os
import json

def test_huggingface_api():
    """Test Hugging Face API connectivity and ticker suggestions."""
    
    print("Testing Hugging Face API...")
    
    # Test configuration
    failed_ticker = "APL"  # Common misspelling of AAPL
    api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    
    common_tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX",
        "BTC-USD", "ETH-USD", "SPY", "QQQ", "VTI", "CSPX.L", "VWRA.L"
    ]
    
    # Check for API token
    hf_token = os.getenv('HF_API_TOKEN', '')
    print(f"HF_API_TOKEN present: {'Yes' if hf_token else 'No (using public API)'}")
    
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
    
    payload = {
        "inputs": {
            "source_sentence": failed_ticker,
            "sentences": common_tickers
        }
    }
    
    print(f"Testing ticker similarity for: {failed_ticker}")
    print(f"API URL: {api_url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=15)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            similarities = response.json()
            print(f"Response Type: {type(similarities)}")
            print(f"Response: {similarities}")
            
            # Process results
            ticker_scores = list(zip(common_tickers, similarities))
            ticker_scores.sort(key=lambda x: x[1], reverse=True)
            
            print(f"\nTop ticker suggestions for '{failed_ticker}':")
            for i, (ticker, score) in enumerate(ticker_scores[:5], 1):
                print(f"  {i}. {ticker} (similarity: {score:.4f})")
            
            # Filter high confidence suggestions
            suggestions = [ticker for ticker, score in ticker_scores[:5] if score > 0.3]
            print(f"\nHigh confidence suggestions (>0.3): {suggestions}")
            
            return True
            
        elif response.status_code == 503:
            print("Model is loading, try again in a few minutes")
            return False
        else:
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("Request timed out")
        return False
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

def test_with_different_inputs():
    """Test with various ticker inputs."""
    test_cases = ["APL", "TESLA", "BTC", "MICROS", "GOOGL"]
    
    for ticker in test_cases:
        print(f"\n{'='*50}")
        print(f"Testing with: {ticker}")
        test_huggingface_api_single(ticker)

def test_huggingface_api_single(failed_ticker):
    """Test single ticker suggestion."""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from ai_utils import try_huggingface_suggestions
        suggestions = try_huggingface_suggestions(failed_ticker)
        print(f"Suggestions for '{failed_ticker}': {suggestions}")
    except Exception as e:
        print(f"Error testing '{failed_ticker}': {e}")

if __name__ == "__main__":
    print("Hugging Face API Test Suite")
    print("="*40)
    
    # Test basic API connectivity
    success = test_huggingface_api()
    
    if success:
        print(f"\n{'='*50}")
        print("Testing integrated function...")
        test_with_different_inputs()
    else:
        print("\nBasic API test failed. Check your connection and try again.")