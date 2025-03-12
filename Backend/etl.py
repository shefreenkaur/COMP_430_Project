# In etl.py
import pandas as pd
from database import SessionLocal, TradeFact, SymbolDimension, TraderDimension, StrategyDimension

def load_trading_data(filepath):
    """Load trading data from CSV file and insert into database"""
    df = pd.read_csv(filepath)
    
    session = SessionLocal()
    
    # Process each row and insert into database
    for _, row in df.iterrows():
        # Check if symbol exists, otherwise create it
        symbol = session.query(SymbolDimension).filter_by(symbol=row['symbol']).first()
        if not symbol:
            symbol = SymbolDimension(
                symbol=row['symbol'],
                asset_class=row.get('asset_class', 'Unknown'),
                sector=row.get('sector', 'Unknown')
            )
            session.add(symbol)
            session.flush()
        
        # Check if trader exists, otherwise create
        trader = session.query(TraderDimension).filter_by(name=row['trader']).first()
        if not trader:
            trader = TraderDimension(
                name=row['trader'],
                team=row.get('team', 'Unknown')
            )
            session.add(trader)
            session.flush()
        
        # Check if strategy exists, otherwise create
        strategy = session.query(StrategyDimension).filter_by(name=row['strategy']).first()
        if not strategy:
            strategy = StrategyDimension(
                name=row['strategy'],
                type=row.get('strategy_type', 'Unknown'),
                risk_profile=row.get('risk_profile', 'Medium')
            )
            session.add(strategy)
            session.flush()
        
        # Create fact record
        trade = TradeFact(
            timestamp=pd.to_datetime(row['timestamp']),
            quantity=row['quantity'],
            price=row['price'],
            total_value=row['quantity'] * row['price'],
            symbol_id=symbol.id,
            trader_id=trader.id,
            strategy_id=strategy.id
        )
        session.add(trade)
    
    session.commit()
    session.close()

def add_sample_trading_data():
    """Add sample trading data for testing"""
    session = SessionLocal()
    
    # Check if we already have data
    if session.query(TradeFact).count() > 0:
        session.close()
        return
    
    # Create sample dimensions
    symbols = [
        SymbolDimension(symbol="AAPL", asset_class="Equity", sector="Technology"),
        SymbolDimension(symbol="MSFT", asset_class="Equity", sector="Technology"),
        SymbolDimension(symbol="BTC", asset_class="Crypto", sector="Currency"),
        SymbolDimension(symbol="EUR/USD", asset_class="Forex", sector="Currency")
    ]
    
    traders = [
        TraderDimension(name="John Smith", team="Alpha"),
        TraderDimension(name="Jane Doe", team="Beta")
    ]
    
    strategies = [
        StrategyDimension(name="Momentum", type="Technical", risk_profile="High"),
        StrategyDimension(name="Value", type="Fundamental", risk_profile="Medium"),
        StrategyDimension(name="Market Neutral", type="Quantitative", risk_profile="Low")
    ]
    
    session.add_all(symbols + traders + strategies)
    session.commit()
    
    # Create sample trade facts
    import datetime
    import random
    
    start_date = datetime.datetime.now() - datetime.timedelta(days=30)
    
    trades = []
    for i in range(100):
        symbol = random.choice(symbols)
        trader = random.choice(traders)
        strategy = random.choice(strategies)
        
        timestamp = start_date + datetime.timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        price = round(random.uniform(10, 1000), 2)
        quantity = random.randint(1, 100)
        
        trade = TradeFact(
            timestamp=timestamp,
            quantity=quantity,
            price=price,
            total_value=price * quantity,
            symbol_id=symbol.id,
            trader_id=trader.id,
            strategy_id=strategy.id
        )
        trades.append(trade)
    
    session.add_all(trades)
    session.commit()
    session.close()