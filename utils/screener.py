import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

def get_fundamentals(ticker: str) -> dict:
    """
    Scrapes Screener.in for fundamental data.
    """
    url = f"https://www.screener.in/company/{ticker}/consolidated/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        # Respectful scraping
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            # Try standalone if consolidated fails or 404
            url = f"https://www.screener.in/company/{ticker}/"
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"Failed to fetch data for {ticker}: Status {response.status_code}")
                return None

        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {'Symbol': ticker}
        
        # Parsing Top Ratios
        ratios = soup.find('ul', {'id': 'top-ratios'})
        if ratios:
            for li in ratios.find_all('li'):
                name_span = li.find('span', {'class': 'name'})
                value_span = li.find('span', {'class': 'number'})
                if name_span and value_span:
                    name = name_span.text.strip()
                    value = value_span.text.strip().replace(',', '')
                    try:
                        data[name] = float(value)
                    except ValueError:
                        data[name] = value

        return data

    except Exception as e:
        print(f"Error scraping {ticker}: {e}")
        return None

def score_stock(fundamentals: dict) -> tuple:
    """
    Basic filtering logic. Returns (True, "Pass") if stock passes criteria.
    Otherwise returns (False, "Reason").
    Criteria:
    - ROE > 15
    - ROCE > 15
    """
    if not fundamentals:
        return False, "No Data"
        
    try:
        roe = float(fundamentals.get('ROE', 0))
        roce = float(fundamentals.get('ROCE', 0))
        
        reasons = []
        if roe <= 15:
            reasons.append(f"ROE {roe} <= 15")
        if roce <= 15:
            reasons.append(f"ROCE {roce} <= 15")
            
        if not reasons:
            return True, "Strong Fundamental"
        else:
            return False, ", ".join(reasons)
    except Exception as e:
        return False, f"Error: {str(e)}"
