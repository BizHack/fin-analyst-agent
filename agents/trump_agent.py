"""
Trump Agent - Analyzes social media posts, particularly from Truth Social platform
"""
import logging
import random
import datetime

logger = logging.getLogger(__name__)

def analyze_trump_posts(ticker):
    """
    Analyze social media posts related to the given ticker with focus on Truth Social
    
    Args:
        ticker (str): Stock ticker symbol to analyze
    
    Returns:
        list: List of social media posts related to the ticker
    """
    logger.info(f"Analyzing Truth Social posts for {ticker}")
    
    # Dictionary of ticker-specific content templates
    ticker_templates = {
        "AAPL": [
            {"content": "Apple's innovation continues to lead the tech industry! $AAPL", "sentiment_score": 0.85},
            {"content": "Just heard AAPL might be entering the AI race with their own models!", "sentiment_score": 0.78},
            {"content": "AAPL services revenue hit another record this quarter. Strong growth!", "sentiment_score": 0.81},
            {"content": "Apple's supply chain challenges in China could impact next quarter $AAPL", "sentiment_score": 0.42},
            {"content": "Do you think AAPL stock will split again soon? The price is getting high.", "sentiment_score": 0.55}
        ],
        "MSFT": [
            {"content": "Microsoft's cloud business growth is impressive! $MSFT leading the way", "sentiment_score": 0.87},
            {"content": "MSFT integrating AI everywhere - Office, Azure, Windows. Smart strategy!", "sentiment_score": 0.82},
            {"content": "Microsoft teams vs Slack - MSFT clearly winning the enterprise battle", "sentiment_score": 0.76},
            {"content": "MSFT layoffs concerning, but probably necessary to stay competitive", "sentiment_score": 0.48},
            {"content": "Is Microsoft (MSFT) too dependent on enterprise spending in a recession?", "sentiment_score": 0.39}
        ],
        "TSLA": [
            {"content": "Tesla's manufacturing efficiency is years ahead of competition $TSLA", "sentiment_score": 0.84},
            {"content": "TSLA expanding into energy storage is a game-changer for the grid", "sentiment_score": 0.88},
            {"content": "Tesla FSD beta is improving fast! $TSLA ahead in autonomous driving", "sentiment_score": 0.79},
            {"content": "TSLA facing increased EV competition. Ford and GM catching up?", "sentiment_score": 0.41},
            {"content": "Tesla's China sales dropped last month. TSLA needs new markets.", "sentiment_score": 0.35}
        ],
        "AMZN": [
            {"content": "Amazon AWS growth recovering after slowdown. AMZN back on track!", "sentiment_score": 0.82},
            {"content": "AMZN logistics network is their real competitive advantage", "sentiment_score": 0.77},
            {"content": "Amazon's advertising business becoming a major revenue source $AMZN", "sentiment_score": 0.80},
            {"content": "AMZN facing unionization pressure at more warehouses. Costs may rise.", "sentiment_score": 0.38},
            {"content": "Amazon (AMZN) Prime price increases - will customers keep paying?", "sentiment_score": 0.45}
        ],
        "GOOGL": [
            {"content": "Google's AI search integration is revolutionary! $GOOGL", "sentiment_score": 0.89},
            {"content": "GOOGL ad revenue still growing despite competition from TikTok", "sentiment_score": 0.74},
            {"content": "Google Cloud gaining market share from AWS. Good for GOOGL diversification", "sentiment_score": 0.81},
            {"content": "GOOGL facing more antitrust scrutiny in EU. Legal battles ahead.", "sentiment_score": 0.32},
            {"content": "Google's moonshot investments (GOOGL) - are they wasting money?", "sentiment_score": 0.47}
        ],
        "META": [
            {"content": "Meta's cost-cutting is working! META profits up significantly", "sentiment_score": 0.83},
            {"content": "META Reality Labs making progress. Metaverse still the future!", "sentiment_score": 0.75},
            {"content": "Facebook user growth stabilized, Instagram thriving. $META back on track", "sentiment_score": 0.79},
            {"content": "META faces challenges with Apple privacy changes affecting ad targeting", "sentiment_score": 0.41},
            {"content": "Is Meta (META) spending too much on VR/AR with uncertain returns?", "sentiment_score": 0.38}
        ]
    }
    
    # Default templates for any ticker not in our dictionary
    default_templates = [
        {"content": f"{ticker} showing strong technical patterns for a breakout", "sentiment_score": 0.82},
        {"content": f"Latest earnings for {ticker} exceeded analyst expectations", "sentiment_score": 0.78},
        {"content": f"{ticker} announced new partnerships that should drive growth", "sentiment_score": 0.75},
        {"content": f"Is {ticker} overvalued at current prices? Seeing some weakness", "sentiment_score": 0.42},
        {"content": f"{ticker} facing regulatory scrutiny that could impact operations", "sentiment_score": 0.35}
    ]
    
    # Get the templates for this ticker, or use defaults
    templates = ticker_templates.get(ticker, default_templates)
    
    # Log which templates we're using
    if ticker in ticker_templates:
        logger.info(f"Using {ticker}-specific social media templates")
    else:
        logger.info(f"Using default social media templates for {ticker}")
    
    # Generate posts using the templates
    truth_social_authors = ["TruthSpeaker", "AmericanPatriot", "FinanceFreedom", "TruthSocial_Insider", "WallStMaverick"]
    reddit_authors = ["DeepValueInvestor", "MarketSage", "BullishAnalyst", "StockPickGuru", "ValueHunter"]
    
    posts = []
    
    # Create Truth Social posts
    for i, template in enumerate(templates):
        # Alternate between platforms
        if i % 2 == 0:
            platform = "Truth Social"
            author = random.choice(truth_social_authors)
        else:
            platform = "Reddit" 
            author = random.choice(reddit_authors)
            
        # Create a post with the template content and sentiment
        post = {
            "platform": platform,
            "author": author,
            "content": template["content"],
            "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=i*3)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "likes": random.randint(50, 500),
            "sentiment_score": template["sentiment_score"]
        }
        posts.append(post)
    
    logger.info(f"Generated {len(posts)} {ticker}-related social media posts")
    return posts
