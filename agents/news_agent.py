"""
News Agent - Analyzes earnings reports and fundamental data
"""
import logging
import yfinance as yf
import datetime
import random

logger = logging.getLogger(__name__)

def analyze_news(ticker):
    """
    Analyze earnings call results and key financial data for the given ticker
    
    Args:
        ticker (str): Stock ticker symbol to analyze
    
    Returns:
        dict: Fundamental data and analysis
    """
    logger.debug(f"Analyzing fundamentals for {ticker}")
    
    try:
        # Get actual data from yfinance
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extract some basic fundamentals
        # Note: Not all of these may be available for every ticker
        market_cap = info.get('marketCap', 'N/A')
        if market_cap != 'N/A':
            market_cap = market_cap / 1_000_000_000  # Convert to billions
            market_cap = round(market_cap, 2)
        
        pe_ratio = info.get('trailingPE', 'N/A')
        if pe_ratio != 'N/A':
            pe_ratio = round(pe_ratio, 2)
        
        dividend_yield = info.get('dividendYield', 'N/A')
        if dividend_yield != 'N/A':
            dividend_yield = round(dividend_yield * 100, 2)  # Convert to percentage
            
        # Get company description and headquarters
        business_description = info.get('longBusinessSummary', f"A publicly traded company with ticker {ticker}.")
        headquarters = info.get('city', 'N/A')
        if headquarters != 'N/A' and info.get('state', 'N/A') != 'N/A':
            headquarters = f"{headquarters}, {info.get('state')}"
        if headquarters != 'N/A' and info.get('country', 'N/A') != 'N/A':
            headquarters = f"{headquarters}, {info.get('country')}"
        
        # Generate years for financial data (current year and 4 previous years)
        current_year = datetime.datetime.now().year
        years = [str(current_year - i) for i in range(5)]
        years.reverse()  # Oldest to newest
        
        # Calculate other financial metrics
        revenue = info.get('totalRevenue', 10000000000) / 1_000_000_000  # Convert to billions
        
        # Mock income statement data 
        # In a production app, this would come from a financial data API or database
        income_statement = [
            {
                "metric": "Revenue",
                "values": [f"${round(revenue * (0.7 + i * 0.1), 2)}B" for i in range(5)]
            },
            {
                "metric": "Gross Profit",
                "values": [f"${round(revenue * (0.7 + i * 0.1) * 0.65, 2)}B" for i in range(5)]
            },
            {
                "metric": "Operating Income",
                "values": [f"${round(revenue * (0.7 + i * 0.1) * 0.3, 2)}B" for i in range(5)]
            },
            {
                "metric": "Net Income",
                "values": [f"${round(revenue * (0.7 + i * 0.1) * 0.2, 2)}B" for i in range(5)]
            },
            {
                "metric": "EPS",
                "values": [f"${round(revenue * (0.7 + i * 0.1) * 0.2 / 1000, 2)}" for i in range(5)]
            }
        ]
        
        # Mock balance sheet data
        balance_sheet = [
            {
                "metric": "Cash & Equivalents",
                "values": [f"${round(revenue * 0.3 * (1 + i * 0.1), 2)}B" for i in range(5)]
            },
            {
                "metric": "Total Assets",
                "values": [f"${round(revenue * 2 * (1 + i * 0.05), 2)}B" for i in range(5)]
            },
            {
                "metric": "Total Debt",
                "values": [f"${round(revenue * 0.8 * (1 - i * 0.05), 2)}B" for i in range(5)]
            },
            {
                "metric": "Total Liabilities",
                "values": [f"${round(revenue * 1.2 * (1 - i * 0.02), 2)}B" for i in range(5)]
            },
            {
                "metric": "Shareholders' Equity",
                "values": [f"${round(revenue * 0.8 * (1 + i * 0.1), 2)}B" for i in range(5)]
            }
        ]
        
        # Mock cash flow data
        cash_flow = [
            {
                "metric": "Operating Cash Flow",
                "values": [f"${round(revenue * 0.25 * (1 + i * 0.1), 2)}B" for i in range(5)]
            },
            {
                "metric": "Capital Expenditure",
                "values": [f"-${round(revenue * 0.1 * (1 + i * 0.05), 2)}B" for i in range(5)]
            },
            {
                "metric": "Free Cash Flow",
                "values": [f"${round(revenue * 0.15 * (1 + i * 0.15), 2)}B" for i in range(5)]
            },
            {
                "metric": "Dividends Paid",
                "values": [f"-${round(revenue * 0.05 * (1 + i * 0.1), 2)}B" for i in range(5)]
            },
            {
                "metric": "Share Repurchases",
                "values": [f"-${round(revenue * 0.08 * (1 + i * 0.05), 2)}B" for i in range(5)]
            }
        ]
        
        # Growth rates
        growth_rates = {
            "revenue": round((float(income_statement[0]["values"][4].replace("$", "").replace("B", "")) / 
                            float(income_statement[0]["values"][3].replace("$", "").replace("B", "")) - 1) * 100, 1),
            "ebitda": round(random.uniform(8.0, 20.0), 1),
            "eps": round((float(income_statement[4]["values"][4].replace("$", "")) / 
                        float(income_statement[4]["values"][3].replace("$", ""))) * 100 - 100, 1)
        }
        
        # Profitability metrics
        profitability = {
            "gross_margin": round(float(income_statement[1]["values"][4].replace("$", "").replace("B", "")) / 
                                float(income_statement[0]["values"][4].replace("$", "").replace("B", "")) * 100, 1),
            "operating_margin": round(float(income_statement[2]["values"][4].replace("$", "").replace("B", "")) / 
                                    float(income_statement[0]["values"][4].replace("$", "").replace("B", "")) * 100, 1),
            "net_margin": round(float(income_statement[3]["values"][4].replace("$", "").replace("B", "")) / 
                                float(income_statement[0]["values"][4].replace("$", "").replace("B", "")) * 100, 1),
            "roe": round(float(income_statement[3]["values"][4].replace("$", "").replace("B", "")) / 
                        float(balance_sheet[4]["values"][4].replace("$", "").replace("B", "")) * 100, 1),
            "roic": round(random.uniform(10.0, 25.0), 1)
        }
        
        # Leverage metrics
        leverage = {
            "debt_equity": round(float(balance_sheet[2]["values"][4].replace("$", "").replace("B", "")) / 
                                float(balance_sheet[4]["values"][4].replace("$", "").replace("B", "")), 2),
            "net_debt_ebitda": round(random.uniform(0.8, 2.5), 2),
            "interest_coverage": round(random.uniform(8.0, 20.0), 2)
        }
        
        # Valuation metrics
        valuation = {
            "pe": pe_ratio if pe_ratio != 'N/A' else round(random.uniform(15.0, 30.0), 2),
            "ev_ebitda": round(random.uniform(10.0, 25.0), 2),
            "pb": round(info.get('priceToBook', random.uniform(2.0, 6.0)), 2),
            "ps": round(info.get('priceToSalesTrailing12Months', random.uniform(2.0, 8.0)), 2)
        }
        
        # Management team (simulated data)
        management = [
            {"name": "John Smith", "title": "CEO"},
            {"name": "Sarah Johnson", "title": "CFO"},
            {"name": "Michael Wong", "title": "CTO"},
            {"name": "Emily Davis", "title": "COO"},
            {"name": "Robert Chen", "title": "CMO"}
        ]
        
        # Generate peer companies in the same sector
        # In production, this would come from a sector ETF or industry classification
        peer_companies = [
            {"name": f"{ticker} Inc.", "ticker": ticker, "market_cap": market_cap, 
             "pe": valuation["pe"], "ev_ebitda": valuation["ev_ebitda"], 
             "revenue_growth": growth_rates["revenue"], "operating_margin": profitability["operating_margin"]},
        ]
        
        # Add 3-5 peer companies
        company_names = ["Alpha Tech", "Beta Solutions", "Gamma Innovations", "Delta Systems", "Epsilon Corp"]
        for i in range(4):
            variation = random.uniform(0.8, 1.2)
            peer_companies.append({
                "name": company_names[i],
                "ticker": f"{company_names[i][:1]}{random.randint(1, 9)}{random.randint(1, 9)}",
                "market_cap": round(market_cap * random.uniform(0.6, 1.4), 2),
                "pe": round(valuation["pe"] * random.uniform(0.9, 1.1), 2),
                "ev_ebitda": round(valuation["ev_ebitda"] * random.uniform(0.9, 1.1), 2),
                "revenue_growth": round(growth_rates["revenue"] * random.uniform(0.8, 1.2), 1),
                "operating_margin": round(profitability["operating_margin"] * random.uniform(0.9, 1.1), 1)
            })
        
        # Analyst ratings
        buy_count = random.randint(10, 25)
        hold_count = random.randint(5, 15)
        sell_count = random.randint(0, 5)
        total_count = buy_count + hold_count + sell_count
        buy_percentage = round(buy_count / total_count * 100)
        
        rating = "Buy"
        if buy_percentage < 40:
            rating = "Sell"
        elif buy_percentage < 70:
            rating = "Hold"
        
        # Price targets
        current_price = info.get('currentPrice', 200)
        if current_price == 'N/A':
            current_price = 200
        
        target_low = round(current_price * 0.85, 2)
        target_high = round(current_price * 1.25, 2)
        target_avg = round((target_high + target_low) / 2, 2)
        current_percentage = round((current_price - target_low) / (target_high - target_low) * 100, 0)
        upside = round((target_avg / current_price - 1) * 100, 1)
        
        # EPS and revenue estimates
        eps_current_quarter = round(random.uniform(0.5, 5.0), 2)
        
        # Recent news articles (simulated)
        recent_news = [
            {
                "title": f"{info.get('longName', ticker)} Reports Strong Q{random.randint(1, 4)} Earnings",
                "date": f"{current_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "summary": f"The company reported earnings of ${eps_current_quarter} per share, beating analyst estimates by {random.randint(5, 20)}%.",
                "source": "MarketWatch",
                "tags": ["Earnings", "Finance"]
            },
            {
                "title": f"{info.get('longName', ticker)} Announces New Product Line",
                "date": f"{current_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "summary": "The company unveiled a new suite of products aimed at expanding its market share in the growing sector.",
                "source": "Bloomberg",
                "tags": ["Products", "Innovation"]
            },
            {
                "title": f"Analysts Raise Price Target for {ticker}",
                "date": f"{current_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "summary": f"Several Wall Street analysts have raised their price targets following the company's recent performance, with a consensus target of ${target_avg}.",
                "source": "CNBC",
                "tags": ["Analysis", "Ratings"]
            }
        ]
        
        # Insider transactions (simulated)
        insider_transactions = [
            {
                "name": "John Smith",
                "title": "CEO",
                "type": "Buy" if random.random() > 0.3 else "Sell",
                "shares": f"{random.randint(5, 50),000}".replace(",", ""),
                "price": round(current_price * random.uniform(0.95, 1.05), 2),
                "date": f"{current_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            },
            {
                "name": "Sarah Johnson",
                "title": "CFO",
                "type": "Buy" if random.random() > 0.3 else "Sell",
                "shares": f"{random.randint(3, 30),000}".replace(",", ""),
                "price": round(current_price * random.uniform(0.95, 1.05), 2),
                "date": f"{current_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            }
        ]
        
        # Ownership structure
        ownership = {
            "institutional": round(random.uniform(60, 85), 1),
            "institutional_change": round(random.uniform(-2, 5), 1),
            "insider": round(random.uniform(5, 20), 1),
            "short_interest": round(random.uniform(1, 8), 1),
            "short_interest_change": round(random.uniform(-1, 2), 1)
        }
        
        # Upcoming catalysts
        catalysts = [
            {
                "event": f"Q{(datetime.datetime.now().month // 3) % 4 + 1} Earnings Release",
                "date": f"{current_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "impact": "High"
            },
            {
                "event": "Annual Investor Day",
                "date": f"{current_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "impact": "Medium"
            },
            {
                "event": "New Product Launch",
                "date": f"{current_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "impact": "Medium-High"
            }
        ]
        
        # Risk factors
        risk_factors = [
            {
                "factor": "Competition Pressure",
                "severity": "Medium",
                "detail": "Facing increasing competition from both established players and new entrants in the market."
            },
            {
                "factor": "Supply Chain Constraints",
                "severity": "Medium-High" if random.random() > 0.5 else "Low",
                "detail": "Global supply chain issues could impact production and delivery timelines."
            },
            {
                "factor": "Regulatory Changes",
                "severity": "High" if random.random() > 0.7 else "Medium",
                "detail": "Potential policy changes could affect operations and compliance costs."
            }
        ]
        
        # Compile comprehensive fundamental data
        fundamentals = {
            "ticker": ticker,
            "company_name": info.get('longName', ticker),
            "market_cap": market_cap,
            "pe_ratio": pe_ratio,
            "dividend_yield": dividend_yield,
            "revenue": round(revenue, 2),
            "eps": info.get('trailingEPS', eps_current_quarter),
            "eps_status": "beating" if info.get('trailingEPS', 0) > info.get('targetMeanPrice', 0) * 0.05 else "missing",
            "guidance": "positive" if info.get('targetMeanPrice', 0) > info.get('currentPrice', 0) else "cautious",
            "sector": info.get('sector', 'Technology'),
            "industry": info.get('industry', 'Software'),
            "52w_high": info.get('fiftyTwoWeekHigh', round(current_price * 1.2, 2)),
            "52w_low": info.get('fiftyTwoWeekLow', round(current_price * 0.8, 2)),
            
            # Additional fields for comprehensive fundamental analysis
            "business_description": business_description,
            "headquarters": headquarters,
            "years": years,
            "income_statement": income_statement,
            "balance_sheet": balance_sheet,
            "cash_flow": cash_flow,
            "growth": growth_rates,
            "profitability": profitability,
            "leverage": leverage,
            "valuation": valuation,
            "management": management,
            "peers": peer_companies,
            "analyst": {
                "buy_count": buy_count,
                "hold_count": hold_count,
                "sell_count": sell_count,
                "total_count": total_count,
                "buy_percentage": buy_percentage,
                "rating": rating
            },
            "price": {
                "current": current_price,
                "target_low": target_low,
                "target_high": target_high,
                "target_avg": target_avg,
                "current_percentage": current_percentage,
                "upside": upside
            },
            "estimates": {
                "eps_current_quarter": eps_current_quarter,
                "eps_next_quarter": round(eps_current_quarter * 1.05, 2),
                "eps_current_year": round(eps_current_quarter * 4, 2),
                "eps_next_year": round(eps_current_quarter * 4 * 1.15, 2),
                "rev_current_quarter": round(revenue / 4, 2),
                "rev_next_quarter": round(revenue / 4 * 1.05, 2),
                "rev_current_year": revenue,
                "rev_next_year": round(revenue * 1.1, 2)
            },
            "news": recent_news,
            "insider_transactions": insider_transactions,
            "ownership": ownership,
            "catalysts": catalysts,
            "risk_factors": risk_factors
        }
        
        return fundamentals
        
    except Exception as e:
        logger.error(f"Error fetching fundamental data for {ticker}: {str(e)}")
        
        # Return a structured response that indicates an error but maintains the expected structure
        return {
            "ticker": ticker,
            "company_name": ticker,
            "market_cap": "N/A",
            "pe_ratio": "N/A",
            "dividend_yield": "N/A",
            "revenue": 0,
            "eps": "N/A",
            "eps_status": "unknown",
            "guidance": "unknown",
            "error": str(e),
            
            # Include minimal required structure for template rendering
            "business_description": f"Information not available for {ticker}.",
            "headquarters": "N/A",
            "years": [str(datetime.datetime.now().year - i) for i in range(5, 0, -1)],
            "income_statement": [],
            "balance_sheet": [],
            "cash_flow": [],
            "growth": {"revenue": 0, "ebitda": 0, "eps": 0},
            "profitability": {"gross_margin": 0, "operating_margin": 0, "net_margin": 0, "roe": 0, "roic": 0},
            "leverage": {"debt_equity": 0, "net_debt_ebitda": 0, "interest_coverage": 0},
            "valuation": {"pe": 0, "ev_ebitda": 0, "pb": 0, "ps": 0},
            "management": [],
            "peers": [],
            "analyst": {"buy_count": 0, "hold_count": 0, "sell_count": 0, "total_count": 0, "buy_percentage": 0, "rating": "N/A"},
            "price": {"current": 0, "target_low": 0, "target_high": 0, "target_avg": 0, "current_percentage": 0, "upside": 0},
            "estimates": {
                "eps_current_quarter": 0, "eps_next_quarter": 0, "eps_current_year": 0, "eps_next_year": 0,
                "rev_current_quarter": 0, "rev_next_quarter": 0, "rev_current_year": 0, "rev_next_year": 0
            },
            "news": [],
            "insider_transactions": [],
            "ownership": {"institutional": 0, "institutional_change": 0, "insider": 0, "short_interest": 0, "short_interest_change": 0},
            "catalysts": [],
            "risk_factors": []
        }
