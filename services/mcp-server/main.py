import os
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import json
from bs4 import BeautifulSoup
import pandas as pd
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Market Data Processor (MCP) Server",
    description="Data Gathering Layer for the finHackers Platform",
    version="1.0.0",
)

# Define data models
class DataResponse(BaseModel):
    source: str
    type: str
    data: List[Dict[str, Any]]
    timestamp: str

class StatusResponse(BaseModel):
    status: str
    uptime: float
    version: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

# Initialize global variables
START_TIME = datetime.now()
SOURCES = {
    "news": ["cnbc", "msn_finance", "yahoo_finance"],
    "social_media": ["reddit", "truth_social"],
    "politician_trades": ["capitol_trades", "senate_stock_watcher"],
    "earnings_calls": ["sec_edgar"],
    "market_prices": ["yahoo_finance", "tradingview"],
    "analyst_reports": ["ubs", "citi", "morgan_stanley", "wells_fargo", "goldman_sachs", "jp_morgan", "barclays", "bofa"]
}

# Cache storage with TTL
CACHE = {}
CACHE_TTL = 300  # seconds

# Helper functions
async def fetch_url(session, url, headers=None):
    try:
        headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        async with session.get(url, headers=headers, timeout=10) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return None

# Specific data fetchers
async def fetch_cnbc_news():
    url = "https://www.cnbc.com/markets/"
    async with aiohttp.ClientSession() as session:
        html = await fetch_url(session, url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        for article in soup.select('.Card-standardBreakerCard'):
            try:
                headline = article.select_one('.Card-title')
                link = article.select_one('a')
                timestamp = article.select_one('.Card-time')
                
                if headline and link:
                    articles.append({
                        'headline': headline.text.strip(),
                        'url': link['href'] if link.has_attr('href') else '',
                        'timestamp': timestamp.text.strip() if timestamp else '',
                        'source': 'CNBC'
                    })
            except Exception as e:
                logger.error(f"Error parsing CNBC article: {str(e)}")
                
        return articles[:10]  # Limit to top 10 articles

async def fetch_reddit_posts(subreddit="wallstreetbets", limit=10, ticker=None):
    if ticker:
        # Search for ticker-specific posts
        url = f"https://www.reddit.com/search.json?q={ticker}%20stock&sort=hot&limit={limit}"
    else:
        # General subreddit posts
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    posts = []
                    
                    for post in data['data']['children']:
                        post_data = post['data']
                        # Extract subreddit from post data
                        post_subreddit = post_data.get('subreddit', subreddit)
                        
                        # Create the post object
                        post_object = {
                            'title': post_data['title'],
                            'author': post_data['author'],
                            'score': post_data['score'],
                            'url': f"https://www.reddit.com{post_data['permalink']}",
                            'created_utc': datetime.fromtimestamp(post_data['created_utc']).isoformat(),
                            'num_comments': post_data['num_comments'],
                            'subreddit': post_subreddit,
                            'source': 'reddit'
                        }
                        
                        # Add text content if available
                        if 'selftext' in post_data and post_data['selftext']:
                            post_object['content'] = post_data['selftext']
                            
                        posts.append(post_object)
                    
                    return posts
                else:
                    logger.error(f"Error fetching Reddit: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching Reddit: {str(e)}")
            return []

async def fetch_truth_social_posts(ticker=None, limit=10):
    """
    Fetch posts from Truth Social related to a specific ticker
    
    Note: This is a placeholder implementation as Truth Social doesn't have a public API.
    To properly implement this function, we would need to use a custom API key
    or alternative data source for Truth Social data.
    """
    # Truth Social search URL (this is conceptual as there isn't a public API)
    # In a real implementation, we would use the official API with authentication
    
    posts = []
    
    # Construct an array of sample data points
    if ticker:
        # This would be replaced with real API calls when authentication is available
        # Simulating result structures for various tickers
        post_count = min(limit, 5)  # Limit the number of posts
        
        for i in range(post_count):
            # Format the creation date for 1-5 days ago
            days_ago = i + 1
            created_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
            
            # Create a post object similar to the Reddit structure but for Truth Social
            post = {
                'id': f"truth_{ticker}_{i}",
                'author': f"truthuser_{100 + i}",
                'created_utc': created_date,
                'url': f"https://truthsocial.com/users/sample/posts/{ticker.lower()}-{i}",
                'source': 'truth_social'
            }
            
            # Add ticker-specific content
            if ticker:
                post['title'] = f"Thoughts on ${ticker} performance"
                post['content'] = f"I've been following ${ticker} closely. The market seems to be reacting to their recent announcements."
            
            posts.append(post)
    
    return posts

# API Routes
@app.get("/")
async def root():
    return {"message": "Welcome to the Market Data Processor (MCP) Server"}

@app.get("/health", response_model=StatusResponse)
async def health_check():
    uptime = (datetime.now() - START_TIME).total_seconds()
    return {
        "status": "healthy",
        "uptime": uptime,
        "version": "1.0.0"
    }

@app.get("/sources")
async def get_sources():
    return SOURCES

@app.get("/news/{source}", response_model=DataResponse)
async def get_news(source: str):
    if source not in SOURCES["news"]:
        raise HTTPException(status_code=404, detail=f"News source '{source}' not found")
    
    # Check cache
    cache_key = f"news_{source}"
    if cache_key in CACHE and (datetime.now() - CACHE[cache_key]["timestamp"]).total_seconds() < CACHE_TTL:
        return CACHE[cache_key]["data"]
    
    # Fetch data
    if source == "cnbc":
        news_data = await fetch_cnbc_news()
    else:
        # Not implemented yet
        news_data = []
    
    # Store in cache
    response = {
        "source": source,
        "type": "news",
        "data": news_data,
        "timestamp": datetime.now().isoformat()
    }
    CACHE[cache_key] = {
        "data": response,
        "timestamp": datetime.now()
    }
    
    return response

@app.get("/social/{source}", response_model=DataResponse)
async def get_social_media(source: str, ticker: Optional[str] = None):
    if source not in SOURCES["social_media"]:
        raise HTTPException(status_code=404, detail=f"Social media source '{source}' not found")
    
    # Check cache - use ticker in cache key if provided
    cache_key = f"social_{source}_{ticker}" if ticker else f"social_{source}"
    if cache_key in CACHE and (datetime.now() - CACHE[cache_key]["timestamp"]).total_seconds() < CACHE_TTL:
        return CACHE[cache_key]["data"]
    
    # Fetch data based on source and ticker
    if source == "reddit":
        social_data = await fetch_reddit_posts(ticker=ticker)
    elif source == "truth_social":
        social_data = await fetch_truth_social_posts(ticker=ticker)
    else:
        # Not implemented yet
        social_data = []
    
    # Store in cache
    response = {
        "source": source,
        "type": "social_media",
        "data": social_data,
        "ticker": ticker,
        "timestamp": datetime.now().isoformat()
    }
    CACHE[cache_key] = {
        "data": response,
        "timestamp": datetime.now()
    }
    
    return response

@app.get("/politician-trades/{source}", response_model=DataResponse)
async def get_politician_trades(source: str):
    if source not in SOURCES["politician_trades"]:
        raise HTTPException(status_code=404, detail=f"Politician trades source '{source}' not found")
    
    # Not implemented yet - placeholder for future implementation
    return {
        "source": source,
        "type": "politician_trades",
        "data": [],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/earnings/{source}", response_model=DataResponse)
async def get_earnings_calls(source: str):
    if source not in SOURCES["earnings_calls"]:
        raise HTTPException(status_code=404, detail=f"Earnings calls source '{source}' not found")
    
    # Not implemented yet - placeholder for future implementation
    return {
        "source": source,
        "type": "earnings_calls",
        "data": [],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/market-prices/{source}", response_model=DataResponse)
async def get_market_prices(source: str):
    if source not in SOURCES["market_prices"]:
        raise HTTPException(status_code=404, detail=f"Market prices source '{source}' not found")
    
    # Not implemented yet - placeholder for future implementation
    return {
        "source": source,
        "type": "market_prices",
        "data": [],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/analyst-reports/{source}", response_model=DataResponse)
async def get_analyst_reports(source: str):
    if source not in SOURCES["analyst_reports"]:
        raise HTTPException(status_code=404, detail=f"Analyst reports source '{source}' not found")
    
    # Not implemented yet - placeholder for future implementation
    return {
        "source": source,
        "type": "analyst_reports",
        "data": [],
        "timestamp": datetime.now().isoformat()
    }

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)