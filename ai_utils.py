import os

def check_api_setup():
    """Check if AI APIs are configured and warn user if not."""
    gemini_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    hf_key = os.getenv('HUGGINGFACE_API_KEY') or os.getenv('HF_API_TOKEN')
    
    if not gemini_key and not hf_key:
        print("⚠️  WARNING: No AI API keys detected!")
        print("   AI-powered ticker suggestions will not be available")
        print("   To enable AI features, set up API keys as described in README.md")
        print("   The application will continue with basic functionality...\n")
    elif not gemini_key:
        print("ℹ️  Note: Google Gemini API not configured (using Hugging Face only)")
    elif not hf_key:
        print("ℹ️  Note: Hugging Face API not configured (using Google Gemini only)")

def get_ai_ticker_suggestions(failed_ticker):
    """Use real AI models to find intelligent ticker suggestions."""
    print("Consulting AI for ticker suggestions...")
    
    # Try Google Gemini API first
    suggestions = try_google_gemini_suggestions(failed_ticker)
    if suggestions:
        return suggestions
    
    # Try Hugging Face API as fallback
    suggestions = try_huggingface_suggestions(failed_ticker)
    if suggestions:
        return suggestions
    
    # Final fallback to pattern matching
    print("AI unavailable, using pattern analysis...")
    return get_pattern_based_suggestions(failed_ticker)

def try_google_gemini_suggestions(failed_ticker):
    """Try Google Gemini API for ticker suggestions."""
    try:
        import requests
        import json
        import os
        
        # Check for API key (user needs to set GEMINI_API_KEY environment variable)
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("⚠️  Google Gemini API key not found!")
            print("   Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
            print("   See README.md for detailed API setup instructions")
            return None
        
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
        prompt = f"""
        The user tried to download stock data for ticker "{failed_ticker}" but it failed.
        Please suggest 5 most likely correct ticker symbols they might have meant.
        
        Consider:
        - Common misspellings (APL -> AAPL)  
        - Missing exchange suffixes (CSPX -> CSPX.L)
        - Company names to tickers (Tesla -> TSLA)
        - Crypto formats (BTC -> BTC-USD)
        
        Respond with ONLY a JSON array of ticker suggestions, like: ["AAPL", "MSFT", "GOOGL"]
        """
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': api_key
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                
                # Extract JSON array from response
                import re
                json_match = re.search(r'\[.*?\]', text, re.DOTALL)
                if json_match:
                    suggestions = json.loads(json_match.group())
                    print(f"Google Gemini suggested: {suggestions}")
                    return suggestions[:5]
    
    except Exception as e:
        print(f"Google Gemini API failed: {e}")
        return None

def try_huggingface_suggestions(failed_ticker):
    """Try Hugging Face API for ticker suggestions."""
    try:
        import requests
        import os
        
        # Use a free text similarity model from Hugging Face
        api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
        
        # Common ticker list for similarity matching
        common_tickers = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX",
            "BTC-USD", "ETH-USD", "SPY", "QQQ", "VTI", "CSPX.L", "VWRA.L"
        ]
        
        # Check for Hugging Face API token
        hf_token = os.getenv('HUGGINGFACE_API_KEY') or os.getenv('HF_API_TOKEN')
        if not hf_token:
            print("⚠️  Hugging Face API key not found!")
            print("   Set HUGGINGFACE_API_KEY environment variable")
            print("   See README.md for detailed API setup instructions")
            return None
            
        headers = {"Authorization": f"Bearer {hf_token}"}
        
        payload = {
            "inputs": {
                "source_sentence": failed_ticker,
                "sentences": common_tickers
            }
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            similarities = response.json()
            # Get top similar tickers
            ticker_scores = list(zip(common_tickers, similarities))
            ticker_scores.sort(key=lambda x: x[1], reverse=True)
            
            suggestions = [ticker for ticker, score in ticker_scores[:5] if score > 0.3]
            if suggestions:
                print(f"Hugging Face suggested: {suggestions}")
                return suggestions
    
    except Exception as e:
        print(f"Hugging Face API failed: {e}")
        return None

def extract_tickers_from_text(text, original_ticker):
    """Extract potential ticker symbols from search result text."""
    import re
    
    suggestions = []
    original_upper = original_ticker.upper()
    
    # Look for ticker-like patterns in the text
    ticker_patterns = [
        r'\b[A-Z]{2,5}\b',           # 2-5 letter codes
        r'\b[A-Z]{2,5}\.[A-Z]{1,2}\b',  # Exchange suffixes
        r'\b[A-Z]{3}-USD\b',        # Crypto patterns
    ]
    
    for pattern in ticker_patterns:
        matches = re.findall(pattern, text.upper())
        for match in matches:
            # Filter to relevant suggestions (similar to original)
            if (len(match) == len(original_upper) or 
                match.startswith(original_upper[:2]) or 
                original_upper in match or 
                match in original_upper):
                suggestions.append(match)
    
    # Add some intelligent guesses based on common patterns
    if original_upper in ['APL', 'APPL']:
        suggestions.insert(0, 'AAPL')
    elif 'TESLA' in original_upper or 'TSL' in original_upper:
        suggestions.insert(0, 'TSLA')
    elif 'BTC' in original_upper or 'BITCOIN' in original_upper:
        suggestions.insert(0, 'BTC-USD')
    
    return list(dict.fromkeys(suggestions))  # Remove duplicates

def get_pattern_based_suggestions(failed_ticker):
    """Intelligent pattern-based suggestions as fallback."""
    suggestions = []
    failed_upper = failed_ticker.upper()
    
    # Smart pattern matching based on ticker characteristics
    if len(failed_upper) == 3 and failed_upper.isalpha():
        # Likely US stock - try common corrections
        suggestions.extend([
            f"{failed_upper}L",  # AAPL pattern
            f"A{failed_upper[1:]}",  # A prefix
            f"{failed_upper}A",  # A suffix
        ])
    
    # European patterns
    if len(failed_upper) <= 5 and '.' not in failed_upper:
        suggestions.extend([
            f"{failed_upper}.L",   # London
            f"{failed_upper}.AS",  # Amsterdam  
            f"{failed_upper}.DE",  # Frankfurt
        ])
    
    # Crypto patterns
    if len(failed_upper) <= 4:
        suggestions.append(f"{failed_upper}-USD")
        
    return list(dict.fromkeys(suggestions))[:5]

def parse_ticker_suggestions(search_results, failed_ticker):
    """Parse AI search results to extract ticker suggestions."""
    suggestions = []
    
    # This would contain logic to extract ticker symbols from search results
    # For now, let's implement a simple fallback approach
    
    # Try common exchange suffixes for European tickers
    if len(failed_ticker) <= 5 and '.' not in failed_ticker:
        exchange_suffixes = ['.L', '.AS', '.DE', '.MI', '.PA']
        suggestions.extend([f"{failed_ticker.upper()}{suffix}" for suffix in exchange_suffixes])
    
    return suggestions[:5]  # Return top 5 suggestions

def get_fallback_suggestions(failed_ticker):
    """Fallback suggestions when AI search fails."""
    failed_upper = failed_ticker.upper()
    
    # Basic corrections for common mistakes
    simple_corrections = {
        'APL': 'AAPL', 'TESLA': 'TSLA', 'MICROSOFT': 'MSFT', 'AMAZON': 'AMZN',
        'GOOGLE': 'GOOGL', 'BTC': 'BTC-USD', 'ETH': 'ETH-USD'
    }
    
    if failed_upper in simple_corrections:
        return [simple_corrections[failed_upper]]
    
    # Try exchange suffixes for unknown tickers
    if '.' not in failed_upper:
        return [f"{failed_upper}.L", f"{failed_upper}.AS", f"{failed_upper}.DE"]
    
    return []