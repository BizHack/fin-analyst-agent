import os
import asyncio
import aiohttp
import logging
from datetime import datetime
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
    "social_media": ["twitter", "reddit", "truth_social"],
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

async def fetch_reddit_posts(subreddit="wallstreetbets", limit=10):
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
                        posts.append({
                            'title': post_data['title'],
                            'author': post_data['author'],
                            'score': post_data['score'],
                            'url': f"https://www.reddit.com{post_data['permalink']}",
                            'created_utc': datetime.fromtimestamp(post_data['created_utc']).isoformat(),
                            'num_comments': post_data['num_comments'],
                            'subreddit': subreddit
                        })
                    
                    return posts
                else:
                    logger.error(f"Error fetching Reddit: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching Reddit: {str(e)}")
            return []

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
async def get_social_media(source: str):
    if source not in SOURCES["social_media"]:
        raise HTTPException(status_code=404, detail=f"Social media source '{source}' not found")
    
    # Check cache
    cache_key = f"social_{source}"
    if cache_key in CACHE and (datetime.now() - CACHE[cache_key]["timestamp"]).total_seconds() < CACHE_TTL:
        return CACHE[cache_key]["data"]
    
    # Fetch data
    if source == "reddit":
        social_data = await fetch_reddit_posts()
    else:
        # Not implemented yet
        social_data = []
    
    # Store in cache
    response = {
        "source": source,
        "type": "social_media",
        "data": social_data,
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