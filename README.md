# finHackers Platform

An advanced AI-powered market intelligence platform that leverages intelligent data processing to provide comprehensive financial insights across multiple data sources.

## Features

- Real-time market trend tracking and analysis
- Multi-source data collection and sentiment analysis
- Advanced visualization of financial data
- Politician trade tracking and analysis
- Social media sentiment analysis
- Fundamental financial data analysis
- Technical indicator analysis
- User authentication and watchlist management
- Alerts for price movements and volume spikes

## Tech Stack

- **Backend**: Python with Flask web framework
- **Database**: PostgreSQL for data persistence
- **Data Retrieval**: yfinance, requests, trafilatura
- **AI Integration**: OpenAI API
- **Frontend**: Modern responsive UI with Tailwind CSS

## Dockerized Deployment

### Prerequisites

- Docker
- Docker Compose
- Git

### Setup and Deployment

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/finhackers.git
   cd finhackers
   ```

2. **Configure environment variables**

   Copy the example environment file and update it with your own settings:

   ```bash
   cp .env.example .env
   ```

   Then edit the `.env` file to include your OpenAI API key and any other environment variables.

3. **Build and start the application**

   ```bash
   # Make the docker commands script executable
   chmod +x docker-commands.sh
   
   # Build the Docker images
   ./docker-commands.sh build
   
   # Start the application
   ./docker-commands.sh up
   ```

   The application will be available at http://localhost:5000

4. **Verify it's working**

   Check the health of the application:

   ```bash
   curl http://localhost:5000/health
   ```

5. **View logs**

   ```bash
   ./docker-commands.sh logs
   ```

6. **Stop the application**

   ```bash
   ./docker-commands.sh down
   ```

### Docker Command Helper

The `docker-commands.sh` script provides convenient shortcuts for common Docker operations:

- `./docker-commands.sh build` - Build the Docker images
- `./docker-commands.sh up` - Start the application
- `./docker-commands.sh down` - Stop the application
- `./docker-commands.sh restart` - Restart the application
- `./docker-commands.sh logs` - Show logs from the containers
- `./docker-commands.sh db-shell` - Access the PostgreSQL database shell
- `./docker-commands.sh app-shell` - Access the application container shell
- `./docker-commands.sh clean` - Remove all containers, images, and volumes
- `./docker-commands.sh help` - Show help message

## Development Setup (Non-Docker)

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install email-validator flask flask-sqlalchemy gunicorn openai psycopg2-binary requests trafilatura yfinance
   ```

3. Set up environment variables:

   ```bash
   export DATABASE_URL=postgresql://username:password@localhost:5432/finhackers
   export OPENAI_API_KEY=your_openai_api_key
   export SESSION_SECRET=your_session_secret
   ```

   On Windows:
   ```
   set DATABASE_URL=postgresql://username:password@localhost:5432/finhackers
   set OPENAI_API_KEY=your_openai_api_key
   set SESSION_SECRET=your_session_secret
   ```

4. Run the application:

   ```bash
   python main.py
   ```

## License

MIT License - Feel free to use, modify, and distribute this code.