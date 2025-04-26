"""
Social Media Aggregator - Analyzes and aggregates social media data from multiple platforms
"""
import logging
import datetime
from agents.trump_agent import analyze_trump_posts

logger = logging.getLogger(__name__)

def analyze_aggregated_social_media(ticker=None):
    """
    Analyze and aggregate social media data from multiple platforms
    
    Args:
        ticker (str, optional): Stock ticker symbol to analyze. If None, analyze overall market sentiment.
    
    Returns:
        dict: Aggregated social media data and analysis
    """
    logger.debug(f"Analyzing aggregated social media data for {'overall market' if ticker is None else ticker}")
    
    # Get individual platform data
    # In a production environment, these would be actual API calls to various platforms
    social_posts = []
    
    # Get data from Trump Agent (which includes Twitter, Reddit, Truth Social)
    if ticker:
        trump_posts = analyze_trump_posts(ticker)
        social_posts.extend(trump_posts)
    else:
        # For overall market sentiment without specific ticker
        platforms = ["AAPL", "TSLA", "MSFT", "AMZN", "NVDA"]
        for platform_ticker in platforms:
            platform_posts = analyze_trump_posts(platform_ticker)
            social_posts.extend(platform_posts)
    
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
        "top_influencers": top_influencers
    }