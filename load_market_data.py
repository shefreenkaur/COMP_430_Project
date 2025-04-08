import yfinance as yf
import pandas as pd
import random
from datetime import datetime, timedelta
import os
import sys

# Add the project directory to the path to ensure imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database models 
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Define database connection
DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Define models 
class SymbolDimension(Base):
    __tablename__ = 'symbol_dim'
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    asset_class = Column(String)
    sector = Column(String)

class TraderDimension(Base):
    __tablename__ = 'trader_dim'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    team = Column(String)

class StrategyDimension(Base):
    __tablename__ = 'strategy_dim'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    risk_profile = Column(String)

class TradeFact(Base):
    __tablename__ = 'trade_facts'
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    quantity = Column(Float)
    price = Column(Float)
    total_value = Column(Float)
    
    # Foreign keys
    symbol_id = Column(Integer, ForeignKey('symbol_dim.id'))
    trader_id = Column(Integer, ForeignKey('trader_dim.id'))
    strategy_id = Column(Integer, ForeignKey('strategy_dim.id'))

# Create tables
Base.metadata.create_all(bind=engine)

def load_market_data():
    session = SessionLocal()
    
    # Define stock symbols and their sectors
    stock_data = [
        {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Cyclical"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Automotive"}
    ]
    
    # Define crypto symbols
    crypto_data = [
        {"symbol": "BTC-USD", "name": "Bitcoin USD", "sector": "Cryptocurrency"},
        {"symbol": "ETH-USD", "name": "Ethereum USD", "sector": "Cryptocurrency"}
    ]
    
    # Define traders
    traders = [
        {"name": "John Smith", "team": "Alpha Team"},
        {"name": "Jane Doe", "team": "Beta Team"},
        {"name": "David Johnson", "team": "Alpha Team"},
        {"name": "Sarah Williams", "team": "Gamma Team"}
    ]
    
    # Define strategies
    strategies = [
        {"name": "Momentum Trading", "type": "Technical", "risk_profile": "High"},
        {"name": "Value Investing", "type": "Fundamental", "risk_profile": "Medium"},
        {"name": "Trend Following", "type": "Technical", "risk_profile": "Medium"},
        {"name": "Mean Reversion", "type": "Quantitative", "risk_profile": "Medium"},
        {"name": "Market Neutral", "type": "Quantitative", "risk_profile": "Low"}
    ]
    
    # Clear existing data if needed
    print("Checking for existing data...")
    if session.query(TradeFact).count() > 0:
        print("Existing trade data found. Skipping data generation.")
        session.close()
        return
    
    print("Creating dimensions...")
    
    # Create symbols in database
    symbols = []
    for data in stock_data:
        symbol = SymbolDimension(
            symbol=data["symbol"],
            asset_class="Equity",
            sector=data["sector"]
        )
        session.add(symbol)
        symbols.append(symbol)
    
    for data in crypto_data:
        symbol = SymbolDimension(
            symbol=data["symbol"],
            asset_class="Crypto",
            sector=data["sector"]
        )
        session.add(symbol)
        symbols.append(symbol)
    
    # Create traders in database
    trader_objs = []
    for data in traders:
        trader = TraderDimension(
            name=data["name"],
            team=data["team"]
        )
        session.add(trader)
        trader_objs.append(trader)
    
    # Create strategies in database
    strategy_objs = []
    for data in strategies:
        strategy = StrategyDimension(
            name=data["name"],
            type=data["type"],
            risk_profile=data["risk_profile"]
        )
        session.add(strategy)
        strategy_objs.append(strategy)
    
    # Commit to get IDs
    session.commit()
    
    print("Downloading market data...")
    
    # Download historical data for each symbol
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 3 months of data
    
    for symbol in symbols:
        try:
            print(f"Downloading data for {symbol.symbol}...")
            
            # Download data from Yahoo Finance
            ticker_data = yf.download(
                symbol.symbol,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                progress=False
            )
            
            # Skip if no data
            if ticker_data.empty:
                print(f"No data available for {symbol.symbol}, skipping...")
                continue
            
            print(f"Processing {len(ticker_data)} days of data for {symbol.symbol}...")
            
            # Process each day's data
            for date, row in ticker_data.iterrows():
                # For each day, create 1-5 trades
                num_trades = random.randint(1, 5)
                
                for _ in range(num_trades):
                    # Pick random trader and strategy
                    trader = random.choice(trader_objs)
                    strategy = random.choice(strategy_objs)
                    
                    # Randomize time during market hours
                    trade_hour = random.randint(9, 16)
                    trade_minute = random.randint(0, 59)
                    trade_second = random.randint(0, 59)
                    trade_time = date.replace(hour=trade_hour, minute=trade_minute, second=trade_second)
                    
                    # Get price (use closing price with small variation)
                    price = row['Close'] * random.uniform(0.995, 1.005)
                    
                    # Determine quantity based on asset class
                    if symbol.asset_class == "Crypto":
                        quantity = random.uniform(0.01, 2.0)  # Fractional for crypto
                    else:
                        quantity = random.randint(10, 100)  # Whole shares for stocks
                    
                    # Create trade
                    trade = TradeFact(
                        timestamp=trade_time,
                        quantity=quantity,
                        price=float(price),
                        total_value=float(price * quantity),
                        symbol_id=symbol.id,
                        trader_id=trader.id,
                        strategy_id=strategy.id
                    )
                    
                    session.add(trade)
                
                # Commit after each day to avoid large transactions
                session.commit()
            
            print(f"Added trades for {symbol.symbol}")
            
        except Exception as e:
            print(f"Error processing {symbol.symbol}: {e}")
            session.rollback()
    
    session.close()
    print("Data loading complete!")

if __name__ == "__main__":
    # Install yfinance if not already installed
    try:
        import yfinance
    except ImportError:
        import subprocess
        print("Installing required package: yfinance")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance"])
        import yfinance
    
    load_market_data()