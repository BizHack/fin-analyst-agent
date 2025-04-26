import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import json
import httpx
import pandas as pd
import numpy as np
from pymongo import MongoClient
import chromadb
from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langraph.graph import Graph, StateGraph, END
from langraph.node import Node, StateNode
from langraph.prebuilt.nodes import LoadAndExtractTextFromURL, Process, Chain, Map, Decision
import anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Market Data Processor (MCP) Client",
    description="Processing Layer for the finHackers Platform",
    version="1.0.0",
)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Initialize connection to MongoDB
mongo_client = MongoClient(os.environ.get("MONGODB_URI", "mongodb://mongoadmin:mongopass@mongodb:27017"))
db = mongo_client["finhackers"]

# Initialize ChromaDB client
chroma_client = chromadb.HttpClient(url=os.environ.get("VECTORDB_URL", "http://vectordb:8080"))

# Define data models
class DataRequest(BaseModel):
    source_type: str
    source_name: str
    params: Optional[Dict[str, Any]] = None

class ProcessRequest(BaseModel):
    data_id: str
    process_type: str
    params: Optional[Dict[str, Any]] = None

class StatusResponse(BaseModel):
    status: str
    uptime: float
    version: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

class WorkflowStatus(BaseModel):
    workflow_id: str
    status: str
    created_at: str
    updated_at: str
    progress: float
    details: Optional[Dict[str, Any]] = None

# Initialize global variables
START_TIME = datetime.now()
WORKFLOWS = {}

# Helper functions
async def fetch_data_from_mcp_server(source_type, source_name, params=None):
    """Fetch data from the MCP Server based on source type and name."""
    base_url = os.environ.get("MCP_SERVER_URL", "http://mcp-server:8000")
    url = f"{base_url}/{source_type}/{source_name}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error fetching data from MCP Server: {str(e)}")
            return None

async def process_text_with_anthropic(text, prompt_template):
    """Process text with Anthropic Claude API."""
    try:
        # Prepare the prompt with the template
        full_prompt = prompt_template.format(text=text)
        
        # Call Anthropic API
        # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
        completion = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.0,
            system="You are a financial analyst assistant. Provide accurate, concise analysis of financial information.",
            messages=[
                {"role": "user", "content": full_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(completion.content[0].text)
    except Exception as e:
        logger.error(f"Error processing text with Anthropic: {str(e)}")
        return {"error": str(e)}

async def save_data_to_mongodb(collection_name, data):
    """Save processed data to MongoDB."""
    try:
        collection = db[collection_name]
        
        # Add timestamp
        if isinstance(data, dict):
            data["timestamp"] = datetime.now().isoformat()
            result = collection.insert_one(data)
            return str(result.inserted_id)
        elif isinstance(data, list):
            for item in data:
                item["timestamp"] = datetime.now().isoformat()
            result = collection.insert_many(data)
            return [str(id) for id in result.inserted_ids]
        else:
            return None
    except Exception as e:
        logger.error(f"Error saving data to MongoDB: {str(e)}")
        return None

async def save_to_vectordb(collection_name, documents, metadata=None):
    """Save documents to VectorDB."""
    try:
        # Create collection if it doesn't exist
        try:
            collection = chroma_client.get_collection(collection_name)
        except:
            collection = chroma_client.create_collection(collection_name)
        
        # Process documents
        for i, doc in enumerate(documents):
            doc_metadata = metadata[i] if metadata else {}
            collection.add(
                documents=[doc],
                metadatas=[doc_metadata],
                ids=[f"{collection_name}_{i}_{datetime.now().timestamp()}"]
            )
        
        return True
    except Exception as e:
        logger.error(f"Error saving to VectorDB: {str(e)}")
        return False

# Define Langraph Workflow
def create_social_media_processing_workflow():
    """Create a workflow for processing social media data."""
    
    # Define nodes
    @Node()
    async def fetch_social_media(source, ticker=None):
        """Fetch social media data from MCP Server."""
        params = {}
        if ticker:
            params["ticker"] = ticker
            
        data = await fetch_data_from_mcp_server("social", source, params)
        if not data:
            return {"status": "error", "message": f"Failed to fetch social media data from {source}"}
        return {"status": "success", "data": data, "ticker": ticker}
    
    @Node()
    async def extract_content(data):
        """Extract and clean content from social media posts."""
        if data["status"] != "success":
            return data
        
        posts = data["data"]["data"]
        ticker = data.get("ticker")
        cleaned_posts = []
        
        for post in posts:
            # Create a standardized post object
            cleaned_post = {
                "title": post.get("title", ""),
                "author": post.get("author", ""),
                "content": post.get("content", post.get("selftext", "")),
                "url": post.get("url", ""),
                "created_utc": post.get("created_utc", ""),
                "source": post.get("source", data["data"]["source"]),
                "score": post.get("score", 0),
                "ticker": ticker
            }
            cleaned_posts.append(cleaned_post)
        
        return {
            "status": "success", 
            "posts": cleaned_posts, 
            "ticker": ticker,
            "source": data["data"]["source"]
        }
    
    @Node()
    async def analyze_sentiment(data):
        """Analyze sentiment of social media posts using Anthropic."""
        if data["status"] != "success":
            return data
        
        posts = data["posts"]
        ticker = data.get("ticker")
        source = data.get("source")
        results = []
        
        # Process posts in batches to avoid hitting API limits
        batch_size = 5
        for i in range(0, len(posts), batch_size):
            batch = posts[i:i+batch_size]
            
            # Skip empty content
            batch = [post for post in batch if post.get("content") or post.get("title")]
            
            if not batch:
                continue
                
            # Create a prompt for Claude to analyze all posts in the batch
            prompt = f"""You are a financial sentiment analyzer. Please analyze the sentiment of the following social media posts about {ticker if ticker else 'the market'}.

For each post, provide:
1. A sentiment score from 0 to 1 (0 being extremely negative, 0.5 being neutral, 1 being extremely positive)
2. A short reason for the sentiment score (max 20 words)
3. Key topics mentioned in the post (comma-separated)

Please format your response as a JSON array where each item has these fields: post_index, sentiment_score, reason, topics.

Here are the posts:

"""
            
            for j, post in enumerate(batch):
                prompt += f"\n--- Post {j+1} ---\n"
                if post.get("title"):
                    prompt += f"Title: {post['title']}\n"
                if post.get("content"):
                    prompt += f"Content: {post['content']}\n"
                prompt += f"Source: {post['source']}\n"
                prompt += f"Author: {post['author']}\n"
                
            prompt += "\nAnalysis in JSON format:"
            
            try:
                # Log that we're using Anthropic for sentiment analysis
                logger.info(f"Using Anthropic Claude API for sentiment analysis of {source} posts about {ticker if ticker else 'general market'}")
                
                # Use Claude with JSON response format
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    temperature=0,
                    system="You are a financial sentiment analysis expert. Always respond with valid JSON.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                # Log successful API call
                logger.info(f"Successfully called Anthropic API for sentiment analysis of {len(batch)} posts")
                
                # Parse the response
                analysis = json.loads(response.content[0].text)
                
                # Add analysis to each post
                for item in analysis.get("analysis", []):
                    post_idx = item.get("post_index", 1) - 1
                    if 0 <= post_idx < len(batch):
                        batch[post_idx]["analysis"] = {
                            "sentiment_score": item.get("sentiment_score", 0.5),
                            "reason": item.get("reason", ""),
                            "topics": item.get("topics", "").split(",")
                        }
                
                # Add analyzed posts to results
                results.extend(batch)
                
            except Exception as e:
                logger.error(f"Error analyzing sentiment with Claude: {str(e)}")
                # Add unanalyzed posts to results
                for post in batch:
                    post["analysis"] = {
                        "sentiment_score": 0.5,
                        "reason": "Analysis failed",
                        "topics": []
                    }
                results.extend(batch)
        
        # Calculate overall sentiment
        if results:
            overall_sentiment = sum(post.get("analysis", {}).get("sentiment_score", 0.5) for post in results) / len(results)
            
            # Extract trending topics
            all_topics = []
            for post in results:
                all_topics.extend(post.get("analysis", {}).get("topics", []))
            
            # Count topics
            topic_counts = {}
            for topic in all_topics:
                topic = topic.strip()
                if topic:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            # Get top topics
            trending_topics = sorted(topic_counts.keys(), key=lambda x: topic_counts[x], reverse=True)[:5]
        else:
            overall_sentiment = 0.5
            trending_topics = []
        
        return {
            "status": "success",
            "posts": results,
            "overall_sentiment": overall_sentiment,
            "trending_topics": trending_topics,
            "ticker": ticker,
            "source": source
        }
    
    @Node()
    async def save_to_database(data):
        """Save processed social media data to MongoDB and VectorDB."""
        if data["status"] != "success":
            return data
        
        posts = data["posts"]
        ticker = data.get("ticker")
        source = data.get("source")
        
        # Prepare data for MongoDB
        mongo_data = {
            "type": "social_media",
            "source": source,
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "overall_sentiment": data["overall_sentiment"],
            "trending_topics": data["trending_topics"],
            "posts": posts
        }
        
        # Save to MongoDB
        try:
            result = db.social_media_data.insert_one(mongo_data)
            mongo_id = str(result.inserted_id)
            logger.info(f"Saved to MongoDB with ID: {mongo_id}")
        except Exception as e:
            logger.error(f"Error saving to MongoDB: {str(e)}")
            mongo_id = None
        
        # Prepare data for VectorDB
        documents = []
        metadata = []
        for post in posts:
            # Create document text
            doc_text = f"Title: {post.get('title', '')}\n"
            doc_text += f"Source: {post.get('source', '')}\n"
            doc_text += f"Author: {post.get('author', '')}\n"
            doc_text += f"Ticker: {ticker}\n" if ticker else ""
            doc_text += f"Content: {post.get('content', '')}\n"
            
            # Create metadata
            meta = {
                "title": post.get("title", ""),
                "source": post.get("source", ""),
                "url": post.get("url", ""),
                "created_utc": post.get("created_utc", ""),
                "sentiment": post.get("analysis", {}).get("sentiment_score", 0.5),
                "topics": ",".join(post.get("analysis", {}).get("topics", [])),
                "ticker": ticker
            }
            
            documents.append(doc_text)
            metadata.append(meta)
        
        # Save to VectorDB
        vectordb_success = await save_to_vectordb("social_media", documents, metadata)
        
        return {
            "status": "success", 
            "mongo_id": mongo_id, 
            "vectordb_success": vectordb_success,
            "document_count": len(documents),
            "overall_sentiment": data["overall_sentiment"],
            "trending_topics": data["trending_topics"]
        }
    
    # Create the graph
    workflow = Graph()
    workflow.add_node("fetch_social_media", fetch_social_media)
    workflow.add_node("extract_content", extract_content)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("save_to_database", save_to_database)
    
    # Connect nodes
    workflow.add_edge("fetch_social_media", "extract_content")
    workflow.add_edge("extract_content", "analyze_sentiment")
    workflow.add_edge("analyze_sentiment", "save_to_database")
    
    return workflow

def create_news_processing_workflow():
    """Create a workflow for processing news data."""
    
    # Define nodes
    @Node()
    async def fetch_news(source):
        """Fetch news data from MCP Server."""
        data = await fetch_data_from_mcp_server("news", source)
        if not data:
            return {"status": "error", "message": f"Failed to fetch news from {source}"}
        return {"status": "success", "data": data}
    
    @Node()
    async def extract_content(data):
        """Extract and clean content from news articles."""
        if data["status"] != "success":
            return data
        
        articles = data["data"]["data"]
        cleaned_articles = []
        
        for article in articles:
            cleaned_articles.append({
                "title": article.get("headline", ""),
                "source": article.get("source", ""),
                "url": article.get("url", ""),
                "timestamp": article.get("timestamp", ""),
                "content": article.get("content", "")
            })
        
        return {"status": "success", "articles": cleaned_articles}
    
    @Node()
    async def analyze_sentiment(articles):
        """Analyze sentiment of news articles using Anthropic."""
        if articles["status"] != "success":
            return articles
        
        results = []
        
        for article in articles["articles"]:
            # Skip articles with no content
            if not article.get("content") and not article.get("title"):
                continue
            
            # Use title if content is empty
            text = article.get("content", article.get("title", ""))
            
            # Prepare prompt for sentiment analysis
            prompt = """
            Analyze the sentiment and financial implications of the following news article:
            
            Title: {title}
            Content: {text}
            
            Provide a JSON response with the following structure:
            {{
                "sentiment": "positive"|"neutral"|"negative",
                "sentiment_score": <float between -1.0 and 1.0>,
                "key_entities": [<list of companies, people, or financial instruments mentioned>],
                "financial_implications": <brief analysis of potential market impact>,
                "confidence": <float between 0.0 and 1.0>
            }}
            """.format(title=article.get("title", ""), text=text)
            
            # Log that we're using Anthropic for news analysis
            logger.info(f"Using Anthropic Claude API for news article analysis: title: {article.get('title', '')}")
            
            # Process with Anthropic
            analysis = await process_text_with_anthropic(text, prompt)
            
            # Log successful API call
            logger.info(f"Successfully called Anthropic API for news analysis of article from {article.get('source', 'unknown')}")
            
            # Combine article with analysis
            result = {**article, "analysis": analysis}
            results.append(result)
        
        return {"status": "success", "analyzed_articles": results}
    
    @Node()
    async def save_to_database(analyzed_articles):
        """Save analyzed articles to MongoDB and VectorDB."""
        if analyzed_articles["status"] != "success":
            return analyzed_articles
        
        # Save to MongoDB
        mongo_id = await save_data_to_mongodb("news_analysis", analyzed_articles["analyzed_articles"])
        
        # Prepare documents for VectorDB
        documents = []
        metadata = []
        
        for article in analyzed_articles["analyzed_articles"]:
            # Create document text
            doc_text = f"Title: {article.get('title', '')}\n"
            doc_text += f"Source: {article.get('source', '')}\n"
            doc_text += f"Timestamp: {article.get('timestamp', '')}\n"
            doc_text += f"Content: {article.get('content', '')}\n"
            
            # Create metadata
            meta = {
                "title": article.get("title", ""),
                "source": article.get("source", ""),
                "url": article.get("url", ""),
                "timestamp": article.get("timestamp", ""),
                "sentiment": article.get("analysis", {}).get("sentiment", "neutral"),
                "sentiment_score": article.get("analysis", {}).get("sentiment_score", 0.0)
            }
            
            documents.append(doc_text)
            metadata.append(meta)
        
        # Save to VectorDB
        vectordb_success = await save_to_vectordb("news", documents, metadata)
        
        return {
            "status": "success", 
            "mongo_id": mongo_id, 
            "vectordb_success": vectordb_success,
            "document_count": len(documents)
        }
    
    # Create the graph
    workflow = Graph()
    workflow.add_node("fetch_news", fetch_news)
    workflow.add_node("extract_content", extract_content)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("save_to_database", save_to_database)
    
    # Connect nodes
    workflow.add_edge("fetch_news", "extract_content")
    workflow.add_edge("extract_content", "analyze_sentiment")
    workflow.add_edge("analyze_sentiment", "save_to_database")
    
    return workflow

# API Routes
@app.get("/")
async def root():
    return {"message": "Welcome to the Market Data Processor (MCP) Client"}

@app.get("/health", response_model=StatusResponse)
async def health_check():
    uptime = (datetime.now() - START_TIME).total_seconds()
    return {
        "status": "healthy",
        "uptime": uptime,
        "version": "1.0.0"
    }

@app.post("/process/social-media")
async def process_social_media(background_tasks: BackgroundTasks, request: DataRequest):
    """Process social media data from MCP Server."""
    source_name = request.source_name
    ticker = request.params.get("ticker") if request.params else None
    
    # Generate workflow ID
    workflow_id = f"social_{source_name}_{ticker or 'general'}_{datetime.now().timestamp()}"
    
    # Create and store workflow
    workflow = create_social_media_processing_workflow()
    WORKFLOWS[workflow_id] = {
        "workflow": workflow,
        "status": "created",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "progress": 0.0,
        "details": {}
    }
    
    # Run workflow in background
    async def run_workflow():
        try:
            # Update status
            WORKFLOWS[workflow_id]["status"] = "running"
            WORKFLOWS[workflow_id]["updated_at"] = datetime.now().isoformat()
            
            # Run workflow
            result = await workflow.ainvoke(source_name, ticker=ticker)
            
            # Update status
            WORKFLOWS[workflow_id]["status"] = "completed"
            WORKFLOWS[workflow_id]["updated_at"] = datetime.now().isoformat()
            WORKFLOWS[workflow_id]["progress"] = 1.0
            WORKFLOWS[workflow_id]["details"] = {
                "result": result,
                "completed_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error running social media workflow: {str(e)}")
            # Update status
            WORKFLOWS[workflow_id]["status"] = "failed"
            WORKFLOWS[workflow_id]["updated_at"] = datetime.now().isoformat()
            WORKFLOWS[workflow_id]["details"] = {
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }
    
    # Schedule workflow
    background_tasks.add_task(run_workflow)
    
    return {"message": "Social media processing scheduled", "workflow_id": workflow_id}

@app.post("/process/news")
async def process_news(background_tasks: BackgroundTasks, request: DataRequest):
    """Process news data from MCP Server."""
    source_name = request.source_name
    
    # Generate workflow ID
    workflow_id = f"news_{source_name}_{datetime.now().timestamp()}"
    
    # Create and store workflow
    workflow = create_news_processing_workflow()
    WORKFLOWS[workflow_id] = {
        "workflow": workflow,
        "status": "created",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "progress": 0.0,
        "details": {}
    }
    
    # Run workflow in background
    async def run_workflow():
        try:
            # Update status
            WORKFLOWS[workflow_id]["status"] = "running"
            WORKFLOWS[workflow_id]["updated_at"] = datetime.now().isoformat()
            
            # Run workflow
            result = await workflow.ainvoke(source_name)
            
            # Update status
            WORKFLOWS[workflow_id]["status"] = "completed"
            WORKFLOWS[workflow_id]["updated_at"] = datetime.now().isoformat()
            WORKFLOWS[workflow_id]["progress"] = 1.0
            WORKFLOWS[workflow_id]["details"] = result
        except Exception as e:
            logger.error(f"Error running workflow {workflow_id}: {str(e)}")
            WORKFLOWS[workflow_id]["status"] = "failed"
            WORKFLOWS[workflow_id]["updated_at"] = datetime.now().isoformat()
            WORKFLOWS[workflow_id]["details"] = {"error": str(e)}
    
    background_tasks.add_task(run_workflow)
    
    return {
        "workflow_id": workflow_id,
        "message": f"Processing news from {source_name} started",
        "status": "created"
    }

@app.get("/workflow/{workflow_id}", response_model=WorkflowStatus)
async def get_workflow_status(workflow_id: str):
    """Get status of a workflow."""
    if workflow_id not in WORKFLOWS:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    workflow_data = WORKFLOWS[workflow_id]
    return {
        "workflow_id": workflow_id,
        "status": workflow_data["status"],
        "created_at": workflow_data["created_at"],
        "updated_at": workflow_data["updated_at"],
        "progress": workflow_data["progress"],
        "details": workflow_data.get("details", {})
    }

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)