"""
Social Media Aggregator - Analyzes and aggregates social media data from multiple platforms
"""
import logging
import datetime
import requests
import os
import json
import time

# Import specific platform agents
from agents.trump_agent import analyze_trump_posts

logger = logging.getLogger(__name__)

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

# Environment variables for API connections
MCP_CLIENT_URL = os.environ.get("MCP_CLIENT_URL", "http://localhost:8001")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8000")
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8888")

def fetch_social_media_data(source, ticker=None):
    """
    Fetch social media data from the MCP Server directly for a specific source
    
    Args:
        source (str): Social media source ('reddit' or 'truth_social')
        ticker (str, optional): Stock ticker symbol to analyze
        
    Returns:
        list: Social media posts from the specified source
    """
    logger.info(f"Fetching {source} data for {'overall market' if ticker is None else ticker}")
    
    try:
        # URL for direct API call to MCP Server
        url = f"{MCP_SERVER_URL}/social/{source}"
        params = {"ticker": ticker} if ticker else {}
        
        # Make the API call
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        # Parse response data
        data = response.json()
        posts = data.get("data", [])
        
        logger.info(f"Successfully fetched {len(posts)} posts from {source}")
        return posts
    
    except Exception as e:
        logger.error(f"Error fetching data from {source}: {str(e)}")
        # Use the fallback method if the API call fails
        if source == "truth_social":
            logger.info("Using Trump agent as fallback for Truth Social data")
            return analyze_trump_posts(ticker)
        return []

def analyze_aggregated_social_media(ticker=None):
    """
    Analyze and aggregate social media data from multiple platforms
    
    Args:
        ticker (str, optional): Stock ticker symbol to analyze. If None, analyze overall market sentiment.
    
    Returns:
        dict: Aggregated social media data and analysis
    """
    logger.info(f"Analyzing aggregated social media data for {'overall market' if ticker is None else ticker}")
    
    # Track sources for attribution
    sources = []
    
    # Get individual platform data
    social_posts = []
    
    # Try to get data from Reddit
    logger.info("Fetching Reddit data...")
    reddit_posts = fetch_social_media_data("reddit", ticker)
    if reddit_posts:
        social_posts.extend(reddit_posts)
        sources.append("Reddit")
        logger.info(f"Added {len(reddit_posts)} posts from Reddit")
    
    # Try to get data from Truth Social
    logger.info("Fetching Truth Social data...")
    truth_posts = fetch_social_media_data("truth_social", ticker)
    if truth_posts:
        social_posts.extend(truth_posts)
        sources.append("Truth Social")
        logger.info(f"Added {len(truth_posts)} posts from Truth Social")
    
    # If no data from APIs, use fallback to Trump Agent for demonstration
    if not social_posts:
        logger.warning("No data from API calls, using Trump agent as fallback")
        trump_posts = analyze_trump_posts(ticker)
        social_posts.extend(trump_posts)
        sources.append("Truth Social")  # We're using the Trump agent as Truth Social data
        logger.info(f"Added {len(trump_posts)} ticker-specific posts for {ticker} from Truth Social fallback")
    
    # Calculate sentiment statistics
    positive_count = sum(1 for post in social_posts if post.get('sentiment_score', 0) > 0.7)
    neutral_count = sum(1 for post in social_posts if 0.4 <= post.get('sentiment_score', 0) <= 0.7)
    negative_count = sum(1 for post in social_posts if post.get('sentiment_score', 0) < 0.4)
    total_count = len(social_posts)
    
    sentiment_stats = {
        "positive_percentage": round((positive_count / total_count) * 100) if total_count > 0 else 0,
        "neutral_percentage": round((neutral_count / total_count) * 100) if total_count > 0 else 0,
        "negative_percentage": round((negative_count / total_count) * 100) if total_count > 0 else 0,
        "total_posts": total_count
    }
    
    # Platform-specific sentiment
    platform_sentiment = {
        "twitter": "2.8",
        "twitter_positive": 65,
        "twitter_neutral": 25,
        "twitter_negative": 10,
        "reddit": "1.5",
        "reddit_positive": 55,
        "reddit_neutral": 30,
        "reddit_negative": 15,
        "discord": "0.7",
        "discord_positive": 35,
        "discord_neutral": 40,
        "discord_negative": 25,
        "youtube": "2.3",
        "youtube_positive": 60,
        "youtube_neutral": 30,
        "youtube_negative": 10
    }
    
    # Add additional metadata to posts for the overview
    top_posts = []
    for i, post in enumerate(social_posts):
        # Enhance post with additional fields for UI display
        enhanced_post = post.copy()
        enhanced_post['reposts'] = post.get('likes', 0) // 3  # Just for demo
        enhanced_post['influence_score'] = round((post.get('sentiment_score', 0.5) * 2 + post.get('likes', 0) / 100) / 3, 1)
        enhanced_post['ticker'] = ticker if ticker else ['AAPL', 'TSLA', 'MSFT', 'AMZN', 'NVDA'][i % 5]
        top_posts.append(enhanced_post)
    
    # Sort by influence score for top posts
    top_posts = sorted(top_posts, key=lambda x: x.get('influence_score', 0), reverse=True)
    
    # Generate trend data for the last 7 days
    today = datetime.datetime.now()
    dates = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    
    sentiment_trend = {
        "dates": dates,
        "positive": [45, 52, 58, 62, 55, 60, sentiment_stats["positive_percentage"]],
        "neutral": [40, 35, 30, 25, 30, 25, sentiment_stats["neutral_percentage"]],
        "negative": [15, 13, 12, 13, 15, 15, sentiment_stats["negative_percentage"]]
    }
    
    # Top assets data
    top_assets_data = {
        "tickers": ["AAPL", "TSLA", "MSFT", "AMZN", "NVDA"],
        "mentions": [350, 280, 220, 180, 150]
    }
    
    # Top keywords with sentiment
    top_keywords = [
        {"word": "earnings", "size": 22, "sentiment": 2.5, "sentiment_abs": "2.5"},
        {"word": "revenue", "size": 18, "sentiment": 1.8, "sentiment_abs": "1.8"},
        {"word": "growth", "size": 20, "sentiment": 3.2, "sentiment_abs": "3.2"},
        {"word": "layoffs", "size": 16, "sentiment": -2.1, "sentiment_abs": "2.1"},
        {"word": "AI", "size": 24, "sentiment": 4.5, "sentiment_abs": "4.5"},
        {"word": "blockchain", "size": 18, "sentiment": 0.8, "sentiment_abs": "0.8"},
        {"word": "regulation", "size": 16, "sentiment": -1.2, "sentiment_abs": "1.2"},
        {"word": "innovation", "size": 19, "sentiment": 2.8, "sentiment_abs": "2.8"},
        {"word": "competition", "size": 17, "sentiment": -0.5, "sentiment_abs": "0.5"},
        {"word": "launch", "size": 18, "sentiment": 2.3, "sentiment_abs": "2.3"},
        {"word": "market", "size": 21, "sentiment": 1.1, "sentiment_abs": "1.1"},
        {"word": "bearish", "size": 16, "sentiment": -2.4, "sentiment_abs": "2.4"},
        {"word": "bullish", "size": 19, "sentiment": 3.1, "sentiment_abs": "3.1"},
        {"word": "stock", "size": 20, "sentiment": 0.7, "sentiment_abs": "0.7"},
        {"word": "investors", "size": 17, "sentiment": 1.5, "sentiment_abs": "1.5"}
    ]
    
    # Trending topics
    trending_topics = [
        {
            "title": "AI Integration",
            "description": "Companies incorporating AI into products",
            "sentiment_change": 4.5,
            "sentiment_change_abs": "4.5",
            "mentions": 1240
        },
        {
            "title": "Quarterly Earnings",
            "description": "Tech sector outperforming expectations",
            "sentiment_change": 3.8,
            "sentiment_change_abs": "3.8",
            "mentions": 980
        },
        {
            "title": "Regulatory Concerns",
            "description": "New antitrust investigations announced",
            "sentiment_change": -2.3,
            "sentiment_change_abs": "2.3",
            "mentions": 760
        },
        {
            "title": "Green Energy",
            "description": "Renewable investments growing",
            "sentiment_change": 2.1,
            "sentiment_change_abs": "2.1",
            "mentions": 650
        },
        {
            "title": "Supply Chain Issues",
            "description": "Manufacturing delays reported",
            "sentiment_change": -1.8,
            "sentiment_change_abs": "1.8",
            "mentions": 520
        }
    ]
    
    # Top influencers
    top_influencers = [
        {
            "name": "MarketWatcher",
            "platform": "Twitter",
            "impact": 5,
            "rank": 1,
            "followers": "2.3M"
        },
        {
            "name": "FinTechAnalyst",
            "platform": "Twitter",
            "impact": 4,
            "rank": 2,
            "followers": "1.8M"
        },
        {
            "name": "CryptoKing",
            "platform": "Reddit",
            "impact": 4,
            "rank": 3,
            "followers": "950K"
        },
        {
            "name": "WallStreetWiz",
            "platform": "Twitter",
            "impact": 3,
            "rank": 4,
            "followers": "780K"
        },
        {
            "name": "TechInvestor",
            "platform": "YouTube",
            "impact": 3,
            "rank": 5,
            "followers": "670K"
        }
    ]
    
    # Return the complete aggregated data
    return {
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sentiment_stats": sentiment_stats,
        "platform_sentiment": platform_sentiment,
        "top_posts": top_posts,
        "sentiment_trend": sentiment_trend,
        "top_assets_data": top_assets_data,
        "top_keywords": top_keywords,
        "trending_topics": trending_topics,
        "top_influencers": top_influencers,
        "sources": sources,  # Add the data sources used for attribution
        "ticker": ticker if ticker else "overall market"  # Add the ticker for reference
    }