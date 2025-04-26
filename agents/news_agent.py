"""
News Agent - Analyzes earnings reports and fundamental data
"""
import logging
import yfinance as yf

logger = logging.getLogger(__name__)

def analyze_news(ticker):
    """
    Analyze earnings call results and key financial data for the given ticker
    
    Args:
        ticker (str): Stock ticker symbol to analyze
    
    Returns:
        dict: Fundamental data and analysis
    """
    logger.debug(f"Analyzing fundamentals for {ticker}")
    
    try:
        # Get actual data from yfinance
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extract some basic fundamentals
        # Note: Not all of these may be available for every ticker
        market_cap = info.get('marketCap', 'N/A')
        if market_cap != 'N/A':
            market_cap = market_cap / 1_000_000_000  # Convert to billions
            market_cap = round(market_cap, 2)
        
        pe_ratio = info.get('trailingPE', 'N/A')
        if pe_ratio != 'N/A':
            pe_ratio = round(pe_ratio, 2)
        
        dividend_yield = info.get('dividendYield', 'N/A')
        if dividend_yield != 'N/A':
            dividend_yield = round(dividend_yield * 100, 2)  # Convert to percentage
            
        # For demonstration of data structure - in production this would be from earnings reports
        fundamentals = {
            "ticker": ticker,
            "company_name": info.get('longName', ticker),
            "market_cap": market_cap,
            "pe_ratio": pe_ratio,
            "dividend_yield": dividend_yield,
            "revenue": round(info.get('totalRevenue', 0) / 1_000_000_000, 2),  # Convert to billions
            "eps": info.get('trailingEPS', 'N/A'),
            "eps_status": "beating" if info.get('trailingEPS', 0) > info.get('targetMeanPrice', 0) * 0.05 else "missing",
            "guidance": "positive" if info.get('targetMeanPrice', 0) > info.get('currentPrice', 0) else "cautious",
            "sector": info.get('sector', 'N/A'),
            "industry": info.get('industry', 'N/A'),
            "52w_high": info.get('fiftyTwoWeekHigh', 'N/A'),
            "52w_low": info.get('fiftyTwoWeekLow', 'N/A')
        }
        
        return fundamentals
        
    except Exception as e:
        logger.error(f"Error fetching fundamental data for {ticker}: {str(e)}")
        
        # Return a structured response that indicates an error but maintains the expected structure
        return {
            "ticker": ticker,
            "company_name": ticker,
            "market_cap": "N/A",
            "pe_ratio": "N/A",
            "dividend_yield": "N/A",
            "revenue": 0,
            "eps": "N/A",
            "eps_status": "unknown",
            "guidance": "unknown",
            "error": str(e)
        }
