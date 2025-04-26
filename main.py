import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import yfinance as yf
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from data.mock_data import get_market_data, get_politician_posts, get_agent_insights

# MCP Service URLs
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8000")
MCP_CLIENT_URL = os.environ.get("MCP_CLIENT_URL", "http://localhost:8001")
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8888")

# Import the classes from the models file
import models
from models import User, Watchlist, WatchlistStock, Alert, StockFundamental, StockSentiment, PoliticianTrade, TechnicalIndicator, AnalystRating

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create and configure the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
models.db.init_app(app)

# Create database tables
with app.app_context():
    models.db.create_all()
    
# User Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
            
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        # Add user to database
        models.db.session.add(new_user)
        models.db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if user exists
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))
        
        # Store user in session
        session['user_id'] = user.id
        
        flash('Login successful!', 'success')
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Log out the current user."""
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Helper function to check if user is logged in
def is_logged_in():
    return 'user_id' in session

# Helper function to get current user
def get_current_user():
    if is_logged_in():
        return User.query.get(session['user_id'])
    return None

@app.route('/')
def index():
    """Render the main page with all required data."""
    # Get market data for quick section
    market_data = get_market_data()
    
    # Get politician posts for quick section
    politician_posts = get_politician_posts()
    
    # Get agent insights for quick section
    agent_insights = get_agent_insights()
    
    return render_template('index.html', 
                           market_data=market_data,
                           politician_posts=politician_posts,
                           agent_insights=agent_insights)

@app.route('/market_data')
def market_data():
    """Get the latest market data."""
    data = get_market_data()
    return jsonify(data)

@app.route('/analyze_ticker', methods=['POST'])
def analyze_ticker():
    """Analyze a ticker symbol based on the tab type."""
    ticker = request.form.get('ticker', 'AAPL')
    tab_type = request.form.get('tab_type', 'sentiment')
    
    try:
        # Get stock data
        stock = yf.Ticker(ticker)
        
        # Different analysis based on tab type
        if tab_type == 'sentiment':
            # Get sentiment data from Backend API
            try:
                response = requests.get(f"{BACKEND_API_URL}/sentiment/{ticker}")
                if response.status_code == 200:
                    sentiment_data = response.json()
                    # If no data returned, trigger data fetch through MCP
                    if not sentiment_data.get("documents") or len(sentiment_data.get("documents", [])) == 0:
                        # Trigger data fetch from MCP Server and processing through MCP Client
                        logger.info(f"No sentiment data found for {ticker}, fetching from sources...")
                        # Process news data for sentiment
                        process_response = requests.post(
                            f"{MCP_CLIENT_URL}/process/news",
                            json={"source_type": "news", "source_name": "cnbc"}
                        )
                        if process_response.status_code == 200:
                            workflow_id = process_response.json().get("workflow_id")
                            logger.info(f"Started processing news for {ticker}, workflow ID: {workflow_id}")
                        
                        # Get existing demo data for now
                        from agents.trump_agent import analyze_trump_posts
                        sentiment_data = {
                            "documents": analyze_trump_posts(ticker),
                            "sentiment_score": 0.65,
                            "trending_topics": ["Earnings Call", "Product Launch", "Market Share"],
                        }
                
                # Build summary based on sentiment score
                sentiment_score = sentiment_data.get("sentiment_score", 0.5)
                if sentiment_score > 0.7:
                    sentiment_type = "strongly positive"
                elif sentiment_score > 0.5:
                    sentiment_type = "moderately positive"
                elif sentiment_score > 0.4:
                    sentiment_type = "neutral"
                elif sentiment_score > 0.2:
                    sentiment_type = "moderately negative"
                else:
                    sentiment_type = "strongly negative"
                
                trending_topics = ", ".join(sentiment_data.get("trending_topics", ["earnings", "product launches"]))
                sentiment_summary = f"Based on recent social media analysis, {ticker} shows {sentiment_type} sentiment with trending discussions about {trending_topics}."
                
                # Use the documents as posts
                posts = sentiment_data.get("documents", [])
                
                return render_template('sentiment.html', 
                                    ticker=ticker, 
                                    posts=posts, 
                                    summary=sentiment_summary)
            
            except Exception as e:
                logger.error(f"Error getting sentiment data from Backend API: {str(e)}")
                # Fallback to existing implementation
                from agents.social_media_aggregator import analyze_aggregated_social_media
                
                # This will combine data from both Reddit and Truth Social
                social_data = analyze_aggregated_social_media(ticker)
                
                # Process the social data
                posts = social_data.get("posts", [])
                sentiment_score = social_data.get("sentiment_score", 0.5)
                
                # Determine sentiment type based on score
                if sentiment_score > 0.7:
                    sentiment_type = "strongly positive"
                elif sentiment_score > 0.5:
                    sentiment_type = "moderately positive"
                elif sentiment_score > 0.4:
                    sentiment_type = "neutral"
                elif sentiment_score > 0.2:
                    sentiment_type = "moderately negative"
                else:
                    sentiment_type = "strongly negative"
                
                trending_topics = ", ".join(social_data.get("trending_topics", ["earnings", "product launches"]))
                sources = ", ".join(social_data.get("sources", ["Reddit", "Truth Social"]))
                
                sentiment_summary = f"Based on recent analysis from {sources}, {ticker} shows {sentiment_type} sentiment with trending discussions about {trending_topics}."
                
                return render_template('sentiment.html', 
                                    ticker=ticker, 
                                    posts=posts, 
                                    summary=sentiment_summary)
            
        elif tab_type == 'politician_trades':
            # Get politician trades from Backend API
            try:
                response = requests.get(f"{BACKEND_API_URL}/politician-trades/{ticker}")
                if response.status_code == 200:
                    trades_data = response.json()
                    trades = trades_data.get("trades", [])
                    
                    # Generate summary
                    if trades:
                        trade_count = len(trades)
                        buy_count = sum(1 for t in trades if t.get("trade_type") == "BUY")
                        sell_count = trade_count - buy_count
                        if buy_count > sell_count:
                            direction = "increased buying"
                            outlook = "positive"
                        elif sell_count > buy_count:
                            direction = "increased selling"
                            outlook = "negative"
                        else:
                            direction = "mixed trading"
                            outlook = "neutral"
                        
                        trade_summary = f"Recent politician trading activity for {ticker} shows {direction} from representatives, suggesting potential {outlook} outlook."
                    else:
                        trade_summary = f"No recent politician trading activity detected for {ticker}."
                    
                    return render_template('politician_trades.html', 
                                        ticker=ticker, 
                                        trades=trades, 
                                        summary=trade_summary)
                
                else:
                    # Fallback to existing implementation
                    from agents.politician_agent import analyze_politician_trades
                    trades = analyze_politician_trades(ticker)
                    trade_summary = f"Recent politician trading activity for {ticker} shows increased buying from representatives on the finance committee, suggesting potential positive outlook."
                    return render_template('politician_trades.html', 
                                        ticker=ticker, 
                                        trades=trades, 
                                        summary=trade_summary)
            
            except Exception as e:
                logger.error(f"Error getting politician trades from Backend API: {str(e)}")
                # Fallback to existing implementation
                from agents.politician_agent import analyze_politician_trades
                trades = analyze_politician_trades(ticker)
                trade_summary = f"Recent politician trading activity for {ticker} shows increased buying from representatives on the finance committee, suggesting potential positive outlook."
                return render_template('politician_trades.html', 
                                    ticker=ticker, 
                                    trades=trades, 
                                    summary=trade_summary)
            
        elif tab_type == 'technical':
            # Get technical analysis from Backend API
            try:
                response = requests.get(f"{BACKEND_API_URL}/technical-analysis/{ticker}")
                if response.status_code == 200:
                    technical_data = response.json()
                    indicators = technical_data.get("indicators", [])
                    support_levels = technical_data.get("support_levels", [])
                    resistance_levels = technical_data.get("resistance_levels", [])
                    volume_analysis = technical_data.get("volume_analysis", {})
                    
                    # Calculate overall signal
                    buy_signals = sum(1 for ind in indicators if ind.get("signal") == "BUY")
                    sell_signals = sum(1 for ind in indicators if ind.get("signal") == "SELL")
                    if buy_signals > sell_signals:
                        pattern = "bullish"
                    elif sell_signals > buy_signals:
                        pattern = "bearish"
                    else:
                        pattern = "neutral"
                    
                    # Format summary
                    support = support_levels[0] if support_levels else "N/A"
                    resistance = resistance_levels[0] if resistance_levels else "N/A"
                    volume_status = volume_analysis.get("volume_status", "NORMAL").replace("_", " ").lower()
                    
                    technical_summary = f"{ticker} is showing a {pattern} pattern with support at ${support} and resistance at ${resistance}. Volume is {volume_status}."
                    
                    return render_template('technical_analysis.html', 
                                        ticker=ticker, 
                                        data=technical_data, 
                                        summary=technical_summary)
                
                else:
                    # Fallback to existing implementation
                    from agents.volume_spike_agent import analyze_volume_spikes
                    technical_data = analyze_volume_spikes(ticker)
                    technical_summary = f"{ticker} is showing a bullish pattern with support at ${technical_data['support']} and resistance at ${technical_data['resistance']}. Volume is {technical_data['volume_status']}."
                    return render_template('technical_analysis.html', 
                                        ticker=ticker, 
                                        data=technical_data, 
                                        summary=technical_summary)
            
            except Exception as e:
                logger.error(f"Error getting technical analysis from Backend API: {str(e)}")
                # Fallback to existing implementation
                from agents.volume_spike_agent import analyze_volume_spikes
                technical_data = analyze_volume_spikes(ticker)
                technical_summary = f"{ticker} is showing a bullish pattern with support at ${technical_data['support']} and resistance at ${technical_data['resistance']}. Volume is {technical_data['volume_status']}."
                return render_template('technical_analysis.html', 
                                    ticker=ticker, 
                                    data=technical_data, 
                                    summary=technical_summary)
            
        elif tab_type == 'fundamentals':
            # Get fundamental analysis from Backend API
            try:
                response = requests.get(f"{BACKEND_API_URL}/fundamental-analysis/{ticker}")
                if response.status_code == 200:
                    fundamentals = response.json()
                    
                    # Format summary
                    revenue = fundamentals.get("revenue_ttm", 0) / 1000000000  # Convert to billions
                    eps = fundamentals.get("eps_ttm", 0)
                    
                    # Determine EPS status based on analyst ratings
                    analyst_ratings = fundamentals.get("analyst_ratings", [])
                    if analyst_ratings:
                        buy_count = sum(1 for r in analyst_ratings if "buy" in r.get("rating", "").lower() or "overweight" in r.get("rating", "").lower())
                        sell_count = sum(1 for r in analyst_ratings if "sell" in r.get("rating", "").lower() or "underweight" in r.get("rating", "").lower())
                        if buy_count > sell_count:
                            eps_status = "exceeding"
                            guidance = "positive"
                        elif sell_count > buy_count:
                            eps_status = "below"
                            guidance = "negative"
                        else:
                            eps_status = "meeting"
                            guidance = "neutral"
                    else:
                        eps_status = "meeting"
                        guidance = "neutral"
                    
                    fundamental_summary = f"{ticker} reported quarterly earnings with revenue of ${revenue:.2f}B, {eps_status} analyst expectations. Guidance for next quarter is {guidance}."
                    
                    return render_template('fundamentals.html', 
                                        ticker=ticker, 
                                        data=fundamentals, 
                                        summary=fundamental_summary)
                
                else:
                    # Fallback to existing implementation
                    from agents.news_agent import analyze_news
                    fundamentals = analyze_news(ticker)
                    fundamental_summary = f"{ticker} reported quarterly earnings with revenue of ${fundamentals['revenue']}B, {fundamentals['eps_status']} analyst expectations. Guidance for next quarter is {fundamentals['guidance']}."
                    return render_template('fundamentals.html', 
                                        ticker=ticker, 
                                        data=fundamentals, 
                                        summary=fundamental_summary)
            
            except Exception as e:
                logger.error(f"Error getting fundamental analysis from Backend API: {str(e)}")
                # Fallback to existing implementation
                from agents.news_agent import analyze_news
                fundamentals = analyze_news(ticker)
                fundamental_summary = f"{ticker} reported quarterly earnings with revenue of ${fundamentals['revenue']}B, {fundamentals['eps_status']} analyst expectations. Guidance for next quarter is {fundamentals['guidance']}."
                return render_template('fundamentals.html', 
                                    ticker=ticker, 
                                    data=fundamentals, 
                                    summary=fundamental_summary)
        
        else:
            return jsonify({"error": "Invalid tab type"}), 400
            
    except Exception as e:
        logger.error(f"Error analyzing ticker {ticker}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/social_media', methods=['GET'])
def social_media_overview():
    """Render the social media overview page with aggregated data."""
    ticker = request.args.get('ticker')
    
    try:
        # Try to get data from the Backend API
        response = requests.get(f"{BACKEND_API_URL}/sentiment/{ticker}")
        if response.status_code == 200:
            sentiment_data = response.json()
            
            # Format the data for the template
            social_data = {
                "ticker": ticker,
                "sentiment_score": sentiment_data.get("sentiment_score", 0.5),
                "trending_topics": sentiment_data.get("trending_topics", []),
                "sources": sentiment_data.get("sources", ["Twitter", "Reddit", "News"]),
                "posts": sentiment_data.get("documents", []),
                "summary": f"Recent sentiment analysis for {ticker} shows a score of {sentiment_data.get('sentiment_score', 0.5):.2f} based on data from {', '.join(sentiment_data.get('sources', ['social media']))}."
            }
        else:
            # Fallback to existing implementation
            from agents.social_media_aggregator import analyze_aggregated_social_media
            social_data = analyze_aggregated_social_media(ticker)
    except Exception as e:
        logger.error(f"Error getting social media data from Backend API: {str(e)}")
        # Fallback to existing implementation
        from agents.social_media_aggregator import analyze_aggregated_social_media
        social_data = analyze_aggregated_social_media(ticker)
    
    # Render the social media overview template with the data
    return render_template('social_media_overview.html', **social_data)

@app.route('/simulate_event', methods=['POST'])
def simulate_event():
    """Simulate a new market event for analysis."""
    event_type = request.form.get('event_type', 'social_post')
    
    if event_type == 'social_post':
        return jsonify({
            "event": "New social media activity detected",
            "analysis": "Increased mention of tech stocks on Reddit with positive sentiment.",
            "impact": "Potential short-term bullish signal for NASDAQ."
        })
    
    elif event_type == 'politician_trade':
        return jsonify({
            "event": "New politician trade detected",
            "analysis": "Senator purchased significant shares in renewable energy sector.",
            "impact": "Possible upcoming legislation favorable to clean energy."
        })
    
    elif event_type == 'market_move':
        return jsonify({
            "event": "Unusual market movement detected",
            "analysis": "SPY experiencing higher than average volume in after-hours trading.",
            "impact": "Preparing for potential volatility at market open."
        })
    
    else:
        return jsonify({"error": "Invalid event type"}), 400

@app.route('/health')
def health_check():
    """Health check endpoint for Docker container monitoring."""
    try:
        # Check database connection
        with models.db.engine.connect() as conn:
            conn.execute("SELECT 1")
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
