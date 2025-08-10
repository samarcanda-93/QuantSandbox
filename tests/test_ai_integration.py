#!/usr/bin/env python3
"""
Test script to verify AI ticker suggestions work.
Usage: 
  set GEMINI_API_KEY=your_key_here
  python tests/test_ai_integration.py APL
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ai_utils

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tests/test_ai_integration.py <ticker>")
        sys.exit(1)
    
    failed_ticker = sys.argv[1]
    print(f"Testing AI suggestions for: {failed_ticker}")
    print(f"API Key present: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")
    
    suggestions = ai_utils.get_ai_ticker_suggestions(failed_ticker)
    print(f"Suggestions: {suggestions}")