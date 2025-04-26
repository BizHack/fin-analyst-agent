import requests
import json
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base URL for the FinHackers application
BASE_URL = "http://127.0.0.1:5000"

def test_market_data():
    """Test the market data endpoint"""
    url = f"{BASE_URL}/market_data"
    logger.info(f"Testing market data endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Market data response status: {response.status_code}")
        logger.info(f"Market data response: {json.dumps(data, indent=2)}")
        
        return data
    except Exception as e:
        logger.error(f"Error testing market data: {str(e)}")
        return None

def test_ticker_analysis(ticker="AAPL", tab_type="sentiment"):
    """Test the ticker analysis endpoint"""
    url = f"{BASE_URL}/analyze_ticker"
    logger.info(f"Testing ticker analysis for {ticker} on tab {tab_type}")
    
    try:
        # The endpoint expects form data, not JSON
        form_data = {"ticker": ticker, "tab_type": tab_type}
        response = requests.post(url, data=form_data, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Ticker analysis response status: {response.status_code}")
        logger.info(f"Ticker analysis response: {json.dumps(data, indent=2)}")
        
        return data
    except Exception as e:
        logger.error(f"Error testing ticker analysis: {str(e)}")
        return None

def test_social_media_overview():
    """Test the social media overview endpoint"""
    url = f"{BASE_URL}/social_media_overview"
    logger.info(f"Testing social media overview endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Social media overview response status: {response.status_code}")
        logger.info(f"Social media overview response: {json.dumps(data, indent=2)}")
        
        return data
    except Exception as e:
        logger.error(f"Error testing social media overview: {str(e)}")
        return None

def main():
    """Run all tests"""
    logger.info("Starting FinHackers API tests")
    
    # 1. Test market data
    market_data = test_market_data()
    time.sleep(1)  # Add a small delay between requests
    
    # 2. Test ticker analysis for AAPL on sentiment tab
    aapl_sentiment = test_ticker_analysis("AAPL", "sentiment")
    time.sleep(1)
    
    # 3. Test ticker analysis for TSLA on sentiment tab
    tsla_sentiment = test_ticker_analysis("TSLA", "sentiment")
    time.sleep(1)
    
    # 4. Test ticker analysis for MSFT on politicians tab
    msft_politicians = test_ticker_analysis("MSFT", "politicians") 
    time.sleep(1)
    
    # 5. Test social media overview
    social_overview = test_social_media_overview()
    
    # Report results
    logger.info("\n=== Test Results Summary ===")
    logger.info(f"Market Data: {'Success' if market_data else 'Failed'}")
    logger.info(f"AAPL Sentiment: {'Success' if aapl_sentiment else 'Failed'}")
    logger.info(f"TSLA Sentiment: {'Success' if tsla_sentiment else 'Failed'}")
    logger.info(f"MSFT Politicians: {'Success' if msft_politicians else 'Failed'}")
    logger.info(f"Social Media Overview: {'Success' if social_overview else 'Failed'}")

if __name__ == "__main__":
    main()