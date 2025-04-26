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
            
            # Process with Anthropic
            analysis = await process_text_with_anthropic(text, prompt)
            
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