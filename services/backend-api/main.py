import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import httpx
from pymongo import MongoClient
import chromadb
from jose import JWTError, jwt
from passlib.context import CryptContext
import pandas as pd
from bson import ObjectId

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FinHackers Backend API",
    description="Backend API for FinHackers Platform",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize MongoDB connection
mongo_client = MongoClient(os.environ.get("MONGODB_URI", "mongodb://mongoadmin:mongopass@mongodb:27017"))
db = mongo_client["finhackers"]

# Initialize ChromaDB client
chroma_client = chromadb.HttpClient(url=os.environ.get("VECTORDB_URL", "http://vectordb:8080"))

# Security settings
SECRET_KEY = os.environ.get("SECRET_KEY", "placeholder_secret_key_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Define data models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class SentimentAnalysis(BaseModel):
    ticker: str
    source: str
    sentiment_score: float
    volume: Optional[int] = None
    trending_topics: Optional[List[str]] = None
    timestamp: str

class PoliticianTrade(BaseModel):
    politician_name: str
    party: Optional[str] = None
    position: Optional[str] = None
    ticker: str
    trade_date: str
    trade_type: str
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    reported_date: Optional[str] = None
    committee: Optional[str] = None

class TechnicalAnalysis(BaseModel):
    ticker: str
    date: str
    indicator_type: str
    value: float
    signal: Optional[str] = None

class FundamentalAnalysis(BaseModel):
    ticker: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    price_to_book: Optional[float] = None
    dividend_yield: Optional[float] = None
    revenue_ttm: Optional[float] = None
    eps_ttm: Optional[float] = None
    profit_margin: Optional[float] = None

class StatusResponse(BaseModel):
    status: str
    uptime: float
    version: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

# Initialize global variables
START_TIME = datetime.now()

# Helper functions for authentication
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    # In a real app, this would query your user database
    # For demo purposes, using a hardcoded user
    if username != "testuser":
        return None
    return UserInDB(
        username=username,
        email="test@example.com",
        full_name="Test User",
        disabled=False,
        hashed_password=get_password_hash("password")
    )

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Helper functions for MongoDB
def serialize_mongo_document(doc):
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc

# API Routes
@app.get("/")
async def root():
    return {"message": "Welcome to the FinHackers Backend API"}

@app.get("/health", response_model=StatusResponse)
async def health_check():
    uptime = (datetime.now() - START_TIME).total_seconds()
    return {
        "status": "healthy",
        "uptime": uptime,
        "version": "1.0.0"
    }

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Sentiment Analysis API Routes
@app.get("/sentiment/{ticker}")
async def get_sentiment_analysis(ticker: str, current_user: User = Depends(get_current_active_user)):
    """Get sentiment analysis for a ticker from both news and social media."""
    try:
        # Get news sentiment data
        news_collection = db["news_analysis"]
        news_cursor = news_collection.find({
            "$or": [
                {"title": {"$regex": ticker, "$options": "i"}},
                {"content": {"$regex": ticker, "$options": "i"}},
                {"analysis.key_entities": {"$regex": ticker, "$options": "i"}}
            ]
        }).sort("timestamp", -1).limit(10)
        
        news_documents = list(map(serialize_mongo_document, news_cursor))
        
        # Get social media sentiment data
        social_collection = db["social_media_data"]
        social_cursor = social_collection.find({
            "ticker": ticker
        }).sort("timestamp", -1).limit(10)
        
        social_documents = list(map(serialize_mongo_document, social_cursor))
        
        # Combine news and social media data
        all_documents = news_documents + social_documents
        
        if not all_documents:
            return {
                "ticker": ticker,
                "sentiment_score": 0.5,
                "sources": [],
                "trending_topics": [],
                "message": "No sentiment data found for this ticker."
            }
        
        # Extract all posts from social media documents
        social_posts = []
        for doc in social_documents:
            if "posts" in doc:
                social_posts.extend(doc["posts"])
        
        # Combine news documents and social posts
        combined_documents = news_documents + social_posts
        
        # Calculate overall sentiment score
        sentiment_scores = []
        
        # Add news sentiment scores
        for doc in news_documents:
            if "analysis" in doc and "sentiment_score" in doc["analysis"]:
                sentiment_scores.append(doc["analysis"]["sentiment_score"])
        
        # Add social media sentiment scores
        for doc in social_documents:
            if "overall_sentiment" in doc:
                # Weight the overall sentiment more heavily
                sentiment_scores.append(doc["overall_sentiment"])
                sentiment_scores.append(doc["overall_sentiment"])
        
        # Add individual social post sentiment scores
        for post in social_posts:
            if "analysis" in post and "sentiment_score" in post["analysis"]:
                sentiment_scores.append(post["analysis"]["sentiment_score"])
        
        # Calculate average sentiment
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.5
        
        # Extract sources
        sources = set()
        for doc in news_documents:
            sources.add(doc.get("source", "unknown"))
        
        for doc in social_documents:
            sources.add(doc.get("source", "unknown"))
        
        # Extract trending topics
        all_topics = []
        
        # From news documents
        for doc in news_documents:
            if "analysis" in doc and "key_entities" in doc["analysis"]:
                all_topics.extend(doc["analysis"]["key_entities"])
        
        # From social media documents
        for doc in social_documents:
            if "trending_topics" in doc:
                all_topics.extend(doc["trending_topics"])
        
        # From individual social posts
        for post in social_posts:
            if "analysis" in post and "topics" in post["analysis"]:
                all_topics.extend(post["analysis"]["topics"])
        
        # Count occurrences of each topic
        topic_counts = {}
        for topic in all_topics:
            if topic and isinstance(topic, str):
                topic = topic.strip()
                if topic:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Sort by count and take top 10
        trending_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        trending_topics = [topic for topic, count in trending_topics]
        
        return {
            "ticker": ticker,
            "sentiment_score": avg_sentiment,
            "sources": list(sources),
            "trending_topics": trending_topics,
            "documents": combined_documents
        }
        
    except Exception as e:
        logger.error(f"Error getting sentiment analysis for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Politician Trades API Routes
@app.get("/politician-trades/{ticker}")
async def get_politician_trades(ticker: str, current_user: User = Depends(get_current_active_user)):
    """Get politician trades for a ticker."""
    try:
        # For demo purposes, returning mock data
        # In production, this would query MongoDB
        return {
            "ticker": ticker,
            "trades": [
                {
                    "politician_name": "Sen. Jane Smith",
                    "party": "Democrat",
                    "position": "Senator",
                    "ticker": ticker,
                    "trade_date": "2025-03-15",
                    "trade_type": "BUY",
                    "amount_min": 15000,
                    "amount_max": 50000,
                    "reported_date": "2025-04-01",
                    "committee": "Finance Committee"
                },
                {
                    "politician_name": "Rep. John Doe",
                    "party": "Republican",
                    "position": "Representative",
                    "ticker": ticker,
                    "trade_date": "2025-03-10",
                    "trade_type": "SELL",
                    "amount_min": 1000,
                    "amount_max": 15000,
                    "reported_date": "2025-03-25",
                    "committee": "Energy and Commerce Committee"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error getting politician trades for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Technical Analysis API Routes
@app.get("/technical-analysis/{ticker}")
async def get_technical_analysis(ticker: str, current_user: User = Depends(get_current_active_user)):
    """Get technical analysis for a ticker."""
    try:
        # For demo purposes, returning mock data
        # In production, this would query MongoDB
        return {
            "ticker": ticker,
            "indicators": [
                {
                    "indicator_type": "RSI",
                    "value": 65.2,
                    "signal": "NEUTRAL",
                    "date": "2025-04-25"
                },
                {
                    "indicator_type": "MACD",
                    "value": 2.1,
                    "signal": "BUY",
                    "date": "2025-04-25"
                },
                {
                    "indicator_type": "Moving Average (50)",
                    "value": 178.45,
                    "signal": "BUY",
                    "date": "2025-04-25"
                },
                {
                    "indicator_type": "Moving Average (200)",
                    "value": 165.32,
                    "signal": "BUY",
                    "date": "2025-04-25"
                }
            ],
            "support_levels": [170.50, 165.25],
            "resistance_levels": [185.75, 190.00],
            "volume_analysis": {
                "current_volume": 35000000,
                "average_volume": 29000000,
                "volume_status": "ABOVE_AVERAGE"
            }
        }
    except Exception as e:
        logger.error(f"Error getting technical analysis for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Fundamental Analysis API Routes
@app.get("/fundamental-analysis/{ticker}")
async def get_fundamental_analysis(ticker: str, current_user: User = Depends(get_current_active_user)):
    """Get fundamental analysis for a ticker."""
    try:
        # For demo purposes, returning mock data
        # In production, this would query MongoDB
        return {
            "ticker": ticker,
            "company_name": f"{ticker} Inc.",
            "sector": "Technology",
            "industry": "Software",
            "market_cap": 2500000000,
            "pe_ratio": 25.3,
            "price_to_book": 8.7,
            "dividend_yield": 1.2,
            "revenue_ttm": 15000000000,
            "eps_ttm": 7.25,
            "profit_margin": 15.8,
            "analyst_ratings": [
                {
                    "firm": "Goldman Sachs",
                    "rating": "Buy",
                    "price_target": 195.00,
                    "analyst": "Sarah Johnson"
                },
                {
                    "firm": "Morgan Stanley",
                    "rating": "Hold",
                    "price_target": 180.00,
                    "analyst": "Michael Chen"
                },
                {
                    "firm": "JP Morgan",
                    "rating": "Overweight",
                    "price_target": 205.00,
                    "analyst": "David Williams"
                }
            ],
            "recent_news": [
                {
                    "title": f"{ticker} Announces New Product Line",
                    "date": "2025-04-20",
                    "source": "CNBC"
                },
                {
                    "title": f"{ticker} Beats Earnings Expectations",
                    "date": "2025-04-15",
                    "source": "Bloomberg"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error getting fundamental analysis for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)