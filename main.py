import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import yfinance as yf
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from data.mock_data import get_market_data, get_politician_posts, get_agent_insights
from agents.trump_agent import analyze_trump_posts
from agents.politician_agent import analyze_politician_trades
from agents.news_agent import analyze_news
from agents.volume_spike_agent import analyze_volume_spikes
from agents.social_media_aggregator import analyze_aggregated_social_media

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
            social_posts = analyze_trump_posts(ticker)
            sentiment_summary = "Based on recent social media analysis, " + ticker + " shows mixed sentiment with trending discussions about quarterly earnings and product launches."
            return render_template('sentiment.html', 
                                   ticker=ticker, 
                                   posts=social_posts, 
                                   summary=sentiment_summary)
            
        elif tab_type == 'politician_trades':
            trades = analyze_politician_trades(ticker)
            trade_summary = "Recent politician trading activity for " + ticker + " shows increased buying from representatives on the finance committee, suggesting potential positive outlook."
            return render_template('politician_trades.html', 
                                   ticker=ticker, 
                                   trades=trades, 
                                   summary=trade_summary)
            
        elif tab_type == 'technical':
            technical_data = analyze_volume_spikes(ticker)
            technical_summary = ticker + " is showing a bullish pattern with support at $" + str(technical_data['support']) + " and resistance at $" + str(technical_data['resistance']) + ". Volume is " + technical_data['volume_status'] + "."
            return render_template('technical_analysis.html', 
                                   ticker=ticker, 
                                   data=technical_data, 
                                   summary=technical_summary)
            
        elif tab_type == 'fundamentals':
            fundamentals = analyze_news(ticker)
            fundamental_summary = ticker + " reported quarterly earnings with revenue of $" + str(fundamentals['revenue']) + "B, " + fundamentals['eps_status'] + " analyst expectations. Guidance for next quarter is " + fundamentals['guidance'] + "."
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
    
    # Get aggregated social media data
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
