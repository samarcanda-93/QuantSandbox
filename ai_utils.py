import os
import yfinance as yf

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
    """Use real AI models to find intelligent ticker suggestions.

    Returns a list of dictionaries: [{ 'ticker': 'AAPL', 'name': 'Apple Inc.' }, ...]
    """
    print("Consulting AI for ticker suggestions...")
    
    raw_suggestions = None
    # Try Google Gemini API first
    raw_suggestions = try_google_gemini_suggestions(failed_ticker)
    if not raw_suggestions:
        # Try Hugging Face API as fallback
        raw_suggestions = try_huggingface_suggestions(failed_ticker)
    if not raw_suggestions:
        # Final fallback to pattern matching
        print("AI unavailable, using pattern analysis...")
        raw_suggestions = get_pattern_based_suggestions(failed_ticker)

    if not raw_suggestions:
        return []

    return enrich_tickers_with_names(raw_suggestions)

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
        The user provided an identifier "{failed_ticker}" that might be a ticker symbol OR a company/ETF name.
        Please suggest the 5 most likely correct ticker symbols they meant, prioritizing major exchanges.

        Consider:
        - Common misspellings (APL -> AAPL)
        - Missing exchange suffixes (CSPX -> CSPX.L)
        - Company/ETF names to tickers (Tesla -> TSLA, SPDR S&P 500 ETF -> SPY)
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
    """Try Hugging Face API for ticker suggestions.

    Accepts either a possible ticker OR a company/ETF/crypto name. We match against a curated
    list of common tickers using sentence similarity, so names like 'Tesla' or 'Apple' should
    score highly for TSLA and AAPL respectively.
    """
    try:
        import requests
        import os
        
        # Use a free text similarity model from Hugging Face
        api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
        
        # Common ticker list for similarity matching (expandable)
        common_tickers = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX",
            "BTC-USD", "ETH-USD", "SPY", "QQQ", "VTI", "CSPX.L", "VWRA.L"
        ]
        # Include some popular non-US ETF tickers & ADRs
        common_tickers += ["IXUS", "VEA", "VWO", "EEM", "IEMG", "SPXL", "SPXS", "TLT", "IEF"]
        
        # Check for Hugging Face API token
        hf_token = os.getenv('HUGGINGFACE_API_KEY') or os.getenv('HF_API_TOKEN')
        if not hf_token:
            print("⚠️  Hugging Face API key not found!")
            print("   Set HUGGINGFACE_API_KEY environment variable")
            print("   See README.md for detailed API setup instructions")
            return None
            
        headers = {"Authorization": f"Bearer {hf_token}"}
        
        payload = {"inputs": {"source_sentence": failed_ticker, "sentences": common_tickers}}
        
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
    """Intelligent pattern-based suggestions as fallback using known valid tickers."""
    suggestions = []
    failed_upper = failed_ticker.upper()
    
    # Name-based quick hints for common firms/ETFs (prioritize known valid tickers)
    name_hints = {
        'TESLA': ['TSLA'],
        'APPLE': ['AAPL'],
        'MICROSOFT': ['MSFT'],
        'ALPHABET': ['GOOGL', 'GOOG'],
        'GOOGLE': ['GOOGL', 'GOOG'],
        'AMAZON': ['AMZN'],
        'META': ['META'],
        'FACEBOOK': ['META'],
        'NVIDIA': ['NVDA'],
        'NETFLIX': ['NFLX'],
        'SPDR S&P 500': ['SPY'],
        'S&P 500': ['SPY', 'IVV', 'VOO'],
        'VANGUARD TOTAL STOCK': ['VTI'],
        'BITCOIN': ['BTC-USD'],
        'ETHEREUM': ['ETH-USD'],
        'ATLANTIC': ['ATCO'],  # Atlantic Power Corporation
    }
    
    # Check for name matches first
    for key, tickers in name_hints.items():
        if key in failed_upper:
            suggestions = tickers + suggestions
            break
    
    # If no name match, suggest popular alternatives based on length/pattern
    if not suggestions:
        if len(failed_upper) <= 4:
            # Short tickers - suggest popular stocks and crypto
            suggestions = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
            if failed_upper.startswith('BTC') or failed_upper.startswith('ETH'):
                suggestions = ['BTC-USD', 'ETH-USD'] + suggestions
        else:
            # Longer input - might be company name, suggest major stocks
            suggestions = ['TSLA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN']

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

def validate_ticker_exists(ticker: str):
    """Check if a ticker exists and has data in yfinance.
    Returns True if ticker is valid, False otherwise.
    """
    try:
        tk = yf.Ticker(ticker)
        # Quick test: try to get recent data (last 5 days)
        hist = tk.history(period="5d")
        return not hist.empty
    except Exception:
        return False

def resolve_ticker_name(ticker: str):
    """Resolve a human-readable security name for a ticker using yfinance.
    Returns None if unavailable quickly.
    """
    try:
        tk = yf.Ticker(ticker)
        # yfinance .info may be slow; handle gracefully
        info = getattr(tk, 'info', None)
        if isinstance(info, dict) and info:
            for key in ('shortName', 'longName', 'name'):
                if key in info and info[key]:
                    return str(info[key])
        return None
    except Exception:
        return None

def generate_market_behavior_analysis(ticker, winning_strategy, mr_sharpe, mom_sharpe, mr_params, mom_params, mr_dd=None, mom_dd=None):
    """Use AI to generate intelligent market behavior analysis based on strategy performance."""
    try:
        import requests
        import json
        import os
        
        # Check for API key
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return get_fallback_market_analysis(ticker, winning_strategy)
        
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
        prompt = f"""
        Analyze {ticker}'s market behavior based on SPECIFIC quantitative backtesting results:
        
        PERFORMANCE DATA:
        - Mean Reversion: Sharpe {mr_sharpe:.3f}, Max Drawdown {f"{mr_dd:.1%}" if mr_dd else "N/A"} (Window: {mr_params[0] if mr_params else 'N/A'}d, Threshold: {f"{mr_params[1]:.1%}" if mr_params and len(mr_params) > 1 else 'N/A'})
        - Momentum: Sharpe {mom_sharpe:.3f}, Max Drawdown {f"{mom_dd:.1%}" if mom_dd else "N/A"} (Window: {mom_params if mom_params else 'N/A'}d)
        - Performance Gap: {abs(mr_sharpe - mom_sharpe):.3f} Sharpe difference
        
        CRITICAL INSTRUCTIONS:
        1. Base analysis ONLY on these specific numbers - cite actual values
        2. Compare both Sharpe ratios AND drawdowns for complete risk assessment
        3. Comment on what the specific parameters tell us (window sizes matter)
        4. If Sharpe difference <0.3, acknowledge both strategies worked reasonably well
        5. Highlight the risk/return trade-off revealed by drawdown vs Sharpe differences
        6. Be precise about what the data shows vs doesn't show
        
        Format as 3-4 bullet points starting with "•" that are:
        - Quantitative and reference specific numbers
        - Focus on risk-adjusted performance comparison
        - Discuss parameter optimization results
        - Avoid broad market characterizations not supported by this specific backtest
        
        Example good analysis: "• Risk-Return Trade-off: While mean reversion achieved X Sharpe vs Y, it came with Z% drawdown compared to W%, suggesting..."
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
                analysis = result['candidates'][0]['content']['parts'][0]['text']
                return analysis.strip()
    
    except Exception as e:
        print(f"AI market analysis failed: {e}")
    
    # Fallback to rule-based analysis
    return get_fallback_market_analysis(ticker, winning_strategy)

def get_fallback_market_analysis(ticker, winning_strategy):
    """Fallback market behavior analysis when AI is unavailable."""
    if winning_strategy == "Mean Reversion":
        return f"""• {ticker} exhibits mean-reverting price behavior patterns
• Asset shows tendency to revert to historical average levels
• Market appears range-bound with predictable price oscillations
• Counter-trend strategies are effective for this asset"""
    else:
        return f"""• {ticker} demonstrates strong trending behavior characteristics
• Momentum persistence suggests directional price movements
• Asset shows sustained trends rather than quick reversals
• Trend-following strategies are well-suited for this market"""

def enrich_tickers_with_names(suggestions):
    """Return list of dicts [{ 'ticker': t, 'name': name_or_none }] from list of ticker strings.
    Only includes tickers that exist and have data in yfinance.
    """
    enriched = []
    seen = set()
    print("Validating ticker suggestions...")
    
    for t in suggestions:
        if not t or t in seen:
            continue
        seen.add(t)
        
        # Validate ticker exists before including it
        if validate_ticker_exists(t):
            name = resolve_ticker_name(t)
            enriched.append({'ticker': t, 'name': name})
            print(f"[OK] {t} - Valid ticker")
        else:
            print(f"[X] {t} - Invalid or no data")
    
    return enriched