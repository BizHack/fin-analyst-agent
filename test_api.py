"""
Test script for triggering social media processing and ticker analysis.
This script tests the connection between MCP Client and MCP Server, focusing on
analyzing Reddit and Truth Social posts for specific tickers using Anthropic Claude API.
"""

import requests
import json
import time
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Environment variables and configuration
MCP_CLIENT_URL = os.environ.get("MCP_CLIENT_URL", "http://localhost:8001")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8000")
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8888")

def test_social_media_processing(ticker="AAPL", source="reddit"):
    """
    Test the social media processing workflow for a specific ticker.
    
    Args:
        ticker (str): Stock ticker symbol to analyze
        source (str): Social media source ('reddit' or 'truth_social')
    """
    logger.info(f"Testing social media processing for {ticker} from {source}")
    
    # Step 1: Trigger the social media processing workflow
    payload = {
        "source_type": "social",
        "source_name": source,
        "params": {"ticker": ticker}
    }
    
    try:
        # Check if MCP Client service is running
        try:
            health_response = requests.head(f"{MCP_CLIENT_URL}/health", timeout=2)
            health_status = health_response.status_code < 400
        except:
            health_status = False
        
        if not health_status:
            logger.warning(f"MCP Client service not available at {MCP_CLIENT_URL}")
            logger.info("Falling back to local social media aggregator...")
            
            # Use local aggregator as fallback
            from agents.social_media_aggregator import analyze_aggregated_social_media
            social_data = analyze_aggregated_social_media(ticker)
            
            sources = social_data.get("sources", [])
            logger.info(f"Successfully retrieved local data from sources: {', '.join(sources) if sources else 'unknown'}")
            
            posts = social_data.get("top_posts", [])
            if posts:
                logger.info(f"Found {len(posts)} posts in local sentiment analysis")
                for i, post in enumerate(posts[:2]):  # Show first 2 posts
                    content = post.get('content', '')
                    if content:
                        content = content[:50] + "..." if len(content) > 50 else content
                    logger.info(f"Post {i+1}: {content} | Score: {post.get('sentiment_score', 'N/A')}")
            return
            
        # If service is running, continue with API call
        response = requests.post(f"{MCP_CLIENT_URL}/process/social-media", json=payload, timeout=5)
        response.raise_for_status()
        
        workflow_id = response.json().get("workflow_id")
        logger.info(f"Started workflow with ID: {workflow_id}")
        
        # Step 2: Monitor the workflow status
        completed = False
        max_attempts = 30
        attempts = 0
        
        while not completed and attempts < max_attempts:
            try:
                status_response = requests.get(f"{MCP_CLIENT_URL}/workflow/{workflow_id}", timeout=5)
                status_data = status_response.json()
                
                status = status_data.get("status")
                progress = status_data.get("progress", 0)
                
                logger.info(f"Workflow status: {status}, progress: {progress:.0%}")
                
                if status == "completed":
                    completed = True
                    logger.info("Workflow completed successfully!")
                    logger.info(f"Details: {json.dumps(status_data.get('details', {}), indent=2)}")
                    break
                elif status == "failed":
                    logger.error(f"Workflow failed: {status_data.get('details', {}).get('error', 'Unknown error')}")
                    break
                
                attempts += 1
                time.sleep(2)
            
            except Exception as e:
                logger.error(f"Error monitoring workflow: {str(e)}")
                break
        
        if not completed:
            logger.warning("Workflow did not complete within the timeout period")
        
    except Exception as e:
        logger.error(f"Error triggering social media processing: {str(e)}")
        logger.info("Falling back to local social media aggregator after error...")
        
        # Use local aggregator as fallback after exception
        try:
            from agents.social_media_aggregator import analyze_aggregated_social_media
            social_data = analyze_aggregated_social_media(ticker)
            
            sources = social_data.get("sources", [])
            logger.info(f"Successfully retrieved local data from sources: {', '.join(sources) if sources else 'unknown'}")
            
            posts = social_data.get("top_posts", [])
            if posts:
                logger.info(f"Found {len(posts)} posts in local sentiment analysis")
                for i, post in enumerate(posts[:2]):  # Show first 2 posts
                    content = post.get('content', '')
                    if content:
                        content = content[:50] + "..." if len(content) > 50 else content
                    logger.info(f"Post {i+1}: {content} | Score: {post.get('sentiment_score', 'N/A')}")
        except Exception as inner_e:
            logger.error(f"Error in fallback mechanism: {str(inner_e)}")

def test_sentiment_analysis(ticker="AAPL"):
    """
    Test fetching sentiment analysis for a specific ticker from the Backend API.
    
    Args:
        ticker (str): Stock ticker symbol to analyze
    """
    logger.info(f"Testing sentiment analysis for {ticker}")
    
    try:
        # Note: In a real environment, this would require authentication
        response = requests.get(f"{BACKEND_API_URL}/sentiment/{ticker}")
        
        if response.status_code == 200:
            sentiment_data = response.json()
            
            logger.info(f"Sentiment score: {sentiment_data.get('sentiment_score', 0.5)}")
            logger.info(f"Trending topics: {', '.join(sentiment_data.get('trending_topics', []))}")
            logger.info(f"Sources: {', '.join(sentiment_data.get('sources', []))}")
            logger.info(f"Document count: {len(sentiment_data.get('documents', []))}")
        else:
            logger.error(f"Error fetching sentiment analysis: {response.status_code} - {response.text}")
    
    except Exception as e:
        logger.error(f"Error fetching sentiment analysis: {str(e)}")

if __name__ == "__main__":
    # Test Reddit social media processing
    test_social_media_processing(ticker="AAPL", source="reddit")
    
    # Test Truth Social media processing
    test_social_media_processing(ticker="AAPL", source="truth_social")
    
    # Wait for processing to complete
    time.sleep(5)
    
    # Test sentiment analysis
    test_sentiment_analysis(ticker="AAPL")