# FinHackers Market Intelligence Platform

FinHackers is an advanced AI-powered market intelligence platform that leverages intelligent data processing to provide comprehensive financial insights across multiple data sources.

## Architecture

The platform is built with a microservices architecture, consisting of several components:

1. **Main Flask Application** - The web interface and API endpoint for the frontend
2. **MCP Server (Data Gathering Layer)** - Responsible for fetching data from various sources
3. **MCP Client (Processing Layer)** - Processes the gathered data using AI
4. **Backend API** - Acts as a gateway between the processed data and the frontend
5. **PostgreSQL Database** - Stores user data, watchlists, and alerts
6. **MongoDB** - Stores processed documents and analysis results
7. **ChromaDB** - Vector database for semantic search and similarity queries

## System Architecture

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│                │     │                │     │                │
│  MCP Server    │────▶│  MCP Client    │────▶│  MongoDB       │
│  (Data Gather) │     │  (Processing)  │     │  (Documents)   │
│                │     │                │     │                │
└────────────────┘     └────────────────┘     └────────────────┘
        │                      │                      │
        │                      │                      │
        │                      ▼                      │
        │              ┌────────────────┐             │
        │              │                │             │
        │              │  ChromaDB      │             │
        │              │  (Vectors)     │             │
        │              │                │             │
        │              └────────────────┘             │
        │                      │                      │
        │                      │                      │
        ▼                      ▼                      ▼
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│                │     │                │     │                │
│  Backend API   │◀───▶│  Flask App     │◀───▶│  PostgreSQL    │
│  (Gateway)     │     │  (Frontend)    │     │  (User Data)   │
│                │     │                │     │                │
└────────────────┘     └────────────────┘     └────────────────┘
                              │
                              │
                              ▼
                      ┌────────────────┐
                      │                │
                      │    Browser     │
                      │                │
                      └────────────────┘
```

## Key Features

- **Multi-Source Data Collection**: Aggregates data from social media, news, politician trades, and market data
- **AI-Powered Analysis**: Processes data using AI models to extract insights
- **Comprehensive Financial Insights**: Technical analysis, fundamental data, sentiment analysis, and more
- **Real-Time Data Processing**: Processes data in real-time for up-to-date insights
- **User Management**: Create watchlists, set alerts, and track favorite stocks

## Tech Stack

- **Backend**: Python (Flask, FastAPI)
- **Frontend**: HTML, CSS, JavaScript (Bootstrap)
- **Databases**: PostgreSQL, MongoDB, ChromaDB
- **AI Processing**: Anthropic Claude, LangGraph, LangChain
- **Containerization**: Docker, Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Anthropic API key (for AI processing)

### Environment Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in the required values
3. Make the helper script executable: `chmod +x docker-commands.sh`

### Running the Application

Start all services:

```bash
./docker-commands.sh up
```

The application will be available at `http://localhost:5000`

### Helper Commands

The `docker-commands.sh` script provides helpful commands for managing the containers:

```bash
# Start all containers in detached mode
./docker-commands.sh up

# Stop and remove all containers
./docker-commands.sh down

# Restart all containers
./docker-commands.sh restart

# View logs for a specific service
./docker-commands.sh logs app

# Execute a bash shell in a container
./docker-commands.sh exec mcp-server

# Rebuild all containers
./docker-commands.sh build

# Remove all containers, images, and volumes
./docker-commands.sh clean
```

## API Endpoints

The Backend API provides several endpoints for accessing financial data:

- `/sentiment/{ticker}` - Get sentiment analysis for a ticker
- `/politician-trades/{ticker}` - Get politician trades for a ticker
- `/technical-analysis/{ticker}` - Get technical analysis for a ticker
- `/fundamental-analysis/{ticker}` - Get fundamental analysis for a ticker

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Anthropic Claude](https://anthropic.com/) for AI processing
- [LangChain](https://www.langchain.com/) for LLM framework
- [FastAPI](https://fastapi.tiangolo.com/) for API development
- [Flask](https://flask.palletsprojects.com/) for web development
- [Docker](https://www.docker.com/) for containerization