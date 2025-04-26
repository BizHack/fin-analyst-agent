import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    watchlists = db.relationship('Watchlist', backref='user', lazy='dynamic')
    alerts = db.relationship('Alert', backref='user', lazy='dynamic')


class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    stocks = db.relationship('WatchlistStock', backref='watchlist', lazy='dynamic', cascade="all, delete-orphan")


class WatchlistStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    watchlist_id = db.Column(db.Integer, db.ForeignKey('watchlist.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)


class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    condition = db.Column(db.String(20), nullable=False)  # 'price_above', 'price_below', 'volume_spike', etc.
    value = db.Column(db.Float, nullable=False)  # Target price or volume level
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_triggered_at = db.Column(db.DateTime, nullable=True)


class StockFundamental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    company_name = db.Column(db.String(128), nullable=False)
    sector = db.Column(db.String(64), nullable=True)
    industry = db.Column(db.String(64), nullable=True)
    market_cap = db.Column(db.Float, nullable=True)
    pe_ratio = db.Column(db.Float, nullable=True)
    price_to_book = db.Column(db.Float, nullable=True)
    dividend_yield = db.Column(db.Float, nullable=True)
    revenue_ttm = db.Column(db.Float, nullable=True)  # Trailing Twelve Months
    eps_ttm = db.Column(db.Float, nullable=True)  # Trailing Twelve Months
    profit_margin = db.Column(db.Float, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StockSentiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    source = db.Column(db.String(20), nullable=False)  # 'twitter', 'reddit', 'news', etc.
    sentiment_score = db.Column(db.Float, nullable=False)  # -1.0 to 1.0
    volume = db.Column(db.Integer, nullable=True)  # Number of mentions
    trending_topics = db.Column(db.Text, nullable=True)  # JSON string of trending topics
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class PoliticianTrade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    politician_name = db.Column(db.String(128), nullable=False)
    party = db.Column(db.String(20), nullable=True)  # 'Democrat', 'Republican', etc.
    position = db.Column(db.String(64), nullable=True)  # 'Senator', 'Representative', etc.
    ticker = db.Column(db.String(10), nullable=False)
    trade_date = db.Column(db.Date, nullable=False)
    trade_type = db.Column(db.String(10), nullable=False)  # 'BUY', 'SELL'
    amount_min = db.Column(db.Float, nullable=True)
    amount_max = db.Column(db.Float, nullable=True)
    reported_date = db.Column(db.Date, nullable=True)
    committee = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TechnicalIndicator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Date, nullable=False)
    indicator_type = db.Column(db.String(20), nullable=False)  # 'RSI', 'MACD', 'Stochastic', etc.
    value = db.Column(db.Float, nullable=False)
    signal = db.Column(db.String(10), nullable=True)  # 'BUY', 'SELL', 'NEUTRAL'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AnalystRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    firm_name = db.Column(db.String(128), nullable=False)
    analyst_name = db.Column(db.String(128), nullable=True)
    rating = db.Column(db.String(20), nullable=False)  # 'Buy', 'Sell', 'Hold', etc.
    previous_rating = db.Column(db.String(20), nullable=True)
    price_target = db.Column(db.Float, nullable=True)
    previous_price_target = db.Column(db.Float, nullable=True)
    rating_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)