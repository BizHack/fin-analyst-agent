"""
Volume Spike Agent - Analyzes technical indicators and price patterns
"""
import logging
import yfinance as yf
import numpy as np

logger = logging.getLogger(__name__)

def analyze_volume_spikes(ticker):
    """
    Analyze technical indicators and price patterns for the given ticker
    
    Args:
        ticker (str): Stock ticker symbol to analyze
    
    Returns:
        dict: Technical analysis data
    """
    logger.debug(f"Analyzing technical indicators for {ticker}")
    
    try:
        # Get actual data from yfinance
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        
        # Calculate basic technical indicators
        # 20-day moving average
        hist['MA20'] = hist['Close'].rolling(window=20).mean()
        
        # Calculate support and resistance levels (simplified)
        support = round(hist['Low'].tail(10).min(), 2)
        resistance = round(hist['High'].tail(10).max(), 2)
        
        # Volume analysis
        avg_volume = hist['Volume'].mean()
        last_volume = hist['Volume'].iloc[-1]
        volume_ratio = last_volume / avg_volume
        
        # Determine volume status
        if volume_ratio > 1.5:
            volume_status = "significantly above average"
        elif volume_ratio > 1.1:
            volume_status = "above average"
        elif volume_ratio < 0.7:
            volume_status = "below average"
        else:
            volume_status = "average"
            
        # Trend determination
        last_close = hist['Close'].iloc[-1]
        ma20_last = hist['MA20'].iloc[-1] if not np.isnan(hist['MA20'].iloc[-1]) else hist['Close'].mean()
        
        if last_close > ma20_last * 1.05:
            trend = "strongly bullish"
        elif last_close > ma20_last:
            trend = "bullish"
        elif last_close < ma20_last * 0.95:
            trend = "strongly bearish"
        elif last_close < ma20_last:
            trend = "bearish"
        else:
            trend = "neutral"
        
        # Prepare data for return
        technical_data = {
            "ticker": ticker,
            "current_price": round(last_close, 2),
            "ma20": round(ma20_last, 2),
            "support": support,
            "resistance": resistance,
            "volume": int(last_volume),
            "avg_volume": int(avg_volume),
            "volume_ratio": round(volume_ratio, 2),
            "volume_status": volume_status,
            "trend": trend,
            # Historical data for potential charting
            "historical_dates": hist.index[-10:].strftime('%Y-%m-%d').tolist(),
            "historical_prices": hist['Close'].tail(10).tolist(),
            "historical_volumes": hist['Volume'].tail(10).astype(int).tolist()
        }
        
        return technical_data
        
    except Exception as e:
        logger.error(f"Error analyzing technical data for {ticker}: {str(e)}")
        
        # Return a structured response that indicates an error but maintains the expected structure
        return {
            "ticker": ticker,
            "current_price": 0,
            "ma20": 0,
            "support": 0,
            "resistance": 0,
            "volume": 0,
            "avg_volume": 0,
            "volume_ratio": 0,
            "volume_status": "unknown",
            "trend": "unknown",
            "historical_dates": [],
            "historical_prices": [],
            "historical_volumes": [],
            "error": str(e)
        }
