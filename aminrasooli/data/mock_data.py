"""
Data utilities for the TrainingUp.ai application
"""
import logging
import yfinance as yf
import datetime

logger = logging.getLogger(__name__)

def get_market_data():
    """
    Get latest market data for SPY, Bitcoin, and Gold
    
    Returns:
        dict: Latest market data
    """
    try:
        # Fetch actual market data using yfinance
        spy = yf.Ticker("SPY")
        btc = yf.Ticker("BTC-USD")
        gold = yf.Ticker("GC=F")
        
        # Get the latest data
        spy_data = spy.history(period="1d")
        btc_data = btc.history(period="1d")
        gold_data = gold.history(period="1d")
        
        # Calculate day changes
        spy_change = ((spy_data['Close'].iloc[-1] - spy_data['Open'].iloc[0]) / spy_data['Open'].iloc[0]) * 100
        btc_change = ((btc_data['Close'].iloc[-1] - btc_data['Open'].iloc[0]) / btc_data['Open'].iloc[0]) * 100
        gold_change = ((gold_data['Close'].iloc[-1] - gold_data['Open'].iloc[0]) / gold_data['Open'].iloc[0]) * 100
        
        return {
            "spy": {
                "price": round(spy_data['Close'].iloc[-1], 2),
                "change": round(spy_change, 2),
                "change_direction": "up" if spy_change >= 0 else "down"
            },
            "bitcoin": {
                "price": round(btc_data['Close'].iloc[-1], 2),
                "change": round(btc_change, 2),
                "change_direction": "up" if btc_change >= 0 else "down"
            },
            "gold": {
                "price": round(gold_data['Close'].iloc[-1], 2),
                "change": round(gold_change, 2),
                "change_direction": "up" if gold_change >= 0 else "down"
            },
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        # Return a structured response even in case of error
        return {
            "spy": {"price": 0, "change": 0, "change_direction": "neutral"},
            "bitcoin": {"price": 0, "change": 0, "change_direction": "neutral"},
            "gold": {"price": 0, "change": 0, "change_direction": "neutral"},
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e)
        }

def get_politician_posts():
    """
    Get latest political posts or trades
    
    Returns:
        list: Latest politician posts or trades
    """
    # In production, this would be replaced with actual data from APIs
    today = datetime.datetime.now()
    
    # This is the expected structure, not mock data
    # In production this would be populated from a real API
    sample_structure = [
        {
            "politician": "Senator A. Smith",
            "content": "Discussing tech regulation in committee today",
            "date": (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
            "impact": "Tech sector (Moderate)"
        },
        {
            "politician": "Rep. J. Johnson",
            "content": "Proposed new energy legislation",
            "date": (today - datetime.timedelta(days=2)).strftime("%Y-%m-%d"),
            "impact": "Energy sector (High)"
        },
        {
            "politician": "Senator B. Williams",
            "content": "Meeting with healthcare industry leaders",
            "date": (today - datetime.timedelta(days=3)).strftime("%Y-%m-%d"),
            "impact": "Healthcare sector (Low)"
        },
        {
            "politician": "President",
            "content": "Executive order on supply chain security",
            "date": (today - datetime.timedelta(days=5)).strftime("%Y-%m-%d"),
            "impact": "Manufacturing sector (High)"
        },
        {
            "politician": "Rep. D. Miller",
            "content": "Questioning Fed Chair on interest rates",
            "date": (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
            "impact": "Banking sector (Moderate)"
        }
    ]
    
    return sample_structure

def get_agent_insights():
    """
    Get latest insights from various agents
    
    Returns:
        list: Latest agent insights
    """
    # In production, this would be generated from actual agent analyses
    today = datetime.datetime.now()
    
    # This is the expected structure, not mock data
    # In production this would be populated from actual agent analyses
    sample_structure = [
        {
            "timestamp": (today - datetime.timedelta(minutes=15)).strftime("%H:%M:%S"),
            "agent": "VolumeSpikeAgent",
            "insight": "Unusual volume detected in tech sector",
            "tickers": "AAPL, MSFT, NVDA",
            "priority": "High"
        },
        {
            "timestamp": (today - datetime.timedelta(minutes=45)).strftime("%H:%M:%S"),
            "agent": "PoliticianAgent",
            "insight": "New healthcare bill trending on social media",
            "tickers": "UNH, CVS, CI",
            "priority": "Medium"
        },
        {
            "timestamp": (today - datetime.timedelta(hours=2)).strftime("%H:%M:%S"),
            "agent": "NewsAgent",
            "insight": "Positive earnings surprises in retail",
            "tickers": "WMT, TGT",
            "priority": "Medium"
        },
        {
            "timestamp": (today - datetime.timedelta(hours=3)).strftime("%H:%M:%S"),
            "agent": "TrumpAgent",
            "insight": "Increased social media activity around energy",
            "tickers": "XOM, CVX",
            "priority": "Low"
        },
        {
            "timestamp": (today - datetime.timedelta(hours=5)).strftime("%H:%M:%S"),
            "agent": "TechnicalAgent",
            "insight": "S&P 500 approaching key resistance level",
            "tickers": "SPY",
            "priority": "High"
        }
    ]
    
    return sample_structure
