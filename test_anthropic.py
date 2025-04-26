"""
Test script to verify Anthropic API integration is working correctly.
This script shows explicit usage of the Anthropic API for sentiment analysis
and logs the API calls in a clear format.
"""
import os
import time
import sys
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='\033[1;36m%(asctime)s - %(name)s - %(levelname)s:\033[0m %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Import the log_anthropic_api_usage function
try:
    from agents.social_media_aggregator import log_anthropic_api_usage
    logger.info("Successfully imported log_anthropic_api_usage")
except ImportError:
    logger.error("Failed to import log_anthropic_api_usage")
    
    # Define it locally if import fails
    def log_anthropic_api_usage(operation, ticker, start_time=None, success=None, error=None):
        """
        Log information about Anthropic API usage for sentiment analysis
        
        Args:
            operation (str): The operation being performed (e.g., "sentiment_analysis")
            ticker (str): The ticker symbol being analyzed
            start_time (float, optional): The start time of the operation (as returned by time.time())
            success (bool, optional): Whether the operation was successful
            error (str, optional): Error message if the operation failed
        """
        # Always print to stdout for immediate visibility
        if start_time and success is not None:
            duration = round((time.time() - start_time) * 1000)  # Convert to milliseconds
            if success:
                message = f"ANTHROPIC API: Successfully completed {operation} for {ticker} in {duration}ms"
                print(f"\033[92m{message}\033[0m")  # Green text
                logger.info(message)
            else:
                message = f"ANTHROPIC API: Failed {operation} for {ticker} after {duration}ms: {error}"
                print(f"\033[91m{message}\033[0m")  # Red text
                logger.error(message)
        else:
            message = f"ANTHROPIC API: Starting {operation} for {ticker} at {time.strftime('%H:%M:%S')}"
            print(f"\033[94m{message}\033[0m")  # Blue text
            logger.info(message)
            return time.time()  # Return start time for later use

# Check for Anthropic API key
anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
if not anthropic_api_key:
    logger.error("ANTHROPIC_API_KEY environment variable is not set!")
    sys.exit(1)

logger.info(f"ANTHROPIC_API_KEY is set (first 5 chars: {anthropic_api_key[:5]}...)")

# Try to import the Anthropic library
try:
    import anthropic
    from anthropic import Anthropic
    
    logger.info("Successfully imported Anthropic library")
    
    # Initialize the Anthropic client
    client = Anthropic(
        api_key=anthropic_api_key,
    )
    logger.info("Successfully initialized Anthropic client")
except ImportError:
    logger.error("Failed to import the Anthropic library. Make sure to install it with: pip install anthropic")
    sys.exit(1)
except Exception as e:
    logger.error(f"Error initializing Anthropic client: {str(e)}")
    sys.exit(1)

def analyze_sentiment_with_anthropic(ticker, content):
    """
    Analyze sentiment of a post about a ticker using Anthropic Claude
    
    Args:
        ticker (str): Stock ticker symbol
        content (str): Content to analyze
        
    Returns:
        dict: Sentiment analysis results
    """
    start_time = log_anthropic_api_usage("sentiment_analysis", ticker)
    
    try:
        logger.info(f"Sending request to Anthropic API for {ticker} sentiment analysis")
        
        # Note that the newest Anthropic model is "claude-3-5-sonnet-20241022"
        # which was released after your knowledge cutoff.
        # Always prefer using claude-3-5-sonnet-20241022 as it is the latest model.
        prompt = f"""
        Analyze the sentiment of this social media post about {ticker} stock.
        
        Post: {content}
        
        Please provide your analysis as JSON with the following fields:
        - sentiment_score: a value between 0 (most negative) and 1 (most positive)
        - key_topics: a list of main topics mentioned in the post
        - relevant_to_stock: boolean indicating if the post is actually relevant to the stock ticker
        - confidence: a value between 0 (lowest) and 1 (highest) indicating confidence in the analysis
        
        JSON response only:
        """
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0,
        )
        
        logger.info("Received response from Anthropic API")
        
        # Extract response content
        result_text = response.content[0].text
        logger.info(f"Raw API response: {result_text}")
        
        # Parse the JSON response
        try:
            # Try to extract just the JSON part from the response
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                result = json.loads(json_str)
            else:
                # If no JSON found, use the full text
                result = json.loads(result_text)
            
            # Extract token usage from the response
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            
            # Log success with token usage
            log_anthropic_api_usage(
                "sentiment_analysis", 
                ticker, 
                start_time, 
                True, 
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
            return result
            
        except json.JSONDecodeError as e:
            log_anthropic_api_usage("sentiment_analysis", ticker, start_time, False, f"JSON parsing error: {e}")
            logger.error(f"Error parsing JSON response: {e}")
            logger.error(f"Response was: {result_text}")
            return {"error": "Failed to parse response", "sentiment_score": 0.5}
    
    except Exception as e:
        log_anthropic_api_usage("sentiment_analysis", ticker, start_time, False, str(e))
        logger.error(f"Error in Anthropic API call: {e}")
        return {"error": str(e), "sentiment_score": 0.5}

def main():
    """Run a test of the Anthropic API integration"""
    
    # Test with a few different tickers and content
    test_cases = [
        {
            "ticker": "AAPL",
            "content": "Apple's latest iPhone has incredible sales numbers, beating all analyst expectations. The stock should soar next quarter!"
        },
        {
            "ticker": "TSLA",
            "content": "Tesla is facing increased competition in the EV market. Their margins are shrinking and production issues continue."
        },
        {
            "ticker": "MSFT",
            "content": "Microsoft Azure cloud growth is steady but not spectacular. The company remains solid but unexciting."
        }
    ]
    
    for case in test_cases:
        ticker = case["ticker"]
        content = case["content"]
        
        print(f"\n\033[1;33m--- Testing sentiment analysis for {ticker} ---\033[0m")
        print(f"Content: {content}")
        
        result = analyze_sentiment_with_anthropic(ticker, content)
        
        print(f"\033[1;33mResults for {ticker}:\033[0m")
        print(json.dumps(result, indent=2))
        print("\033[1;33m---------------------------------\033[0m")
        
        # Wait a bit between requests
        time.sleep(1)
    
    print("\n\033[1;32mAll tests completed!\033[0m")

if __name__ == "__main__":
    main()