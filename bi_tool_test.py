from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import uvicorn
import pandas as pd

# Import database models
from database import SessionLocal, SalesData, TradeFact, SymbolDimension, TraderDimension, StrategyDimension

# ----------------- FASTAPI BACKEND -----------------
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "BI API is running"}

@app.get("/symbols")
def get_symbols(db: Session = Depends(get_db)):
    symbols = db.query(SymbolDimension).all()
    return [{"id": s.id, "symbol": s.symbol, "asset_class": s.asset_class, "sector": s.sector} for s in symbols]

@app.get("/strategies")
def get_strategies(db: Session = Depends(get_db)):
    strategies = db.query(StrategyDimension).all()
    return [{"id": s.id, "name": s.name, "type": s.type, "risk_profile": s.risk_profile} for s in strategies]

@app.get("/trades")
def get_trades(
    skip: int = 0, 
    limit: int = 100,
    start_date: str = None,
    end_date: str = None,
    symbol_id: int = None,
    strategy_id: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        TradeFact.id,
        TradeFact.timestamp,
        TradeFact.quantity,
        TradeFact.price,
        TradeFact.total_value,
        SymbolDimension.symbol,
        SymbolDimension.asset_class,
        TraderDimension.name.label("trader_name"),
        StrategyDimension.name.label("strategy_name")
    ).join(
        SymbolDimension, TradeFact.symbol_id == SymbolDimension.id
    ).join(
        TraderDimension, TradeFact.trader_id == TraderDimension.id
    ).join(
        StrategyDimension, TradeFact.strategy_id == StrategyDimension.id
    )
    
    # Apply filters
    if start_date:
        query = query.filter(TradeFact.timestamp >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(TradeFact.timestamp <= datetime.fromisoformat(end_date))
    if symbol_id:
        query = query.filter(TradeFact.symbol_id == symbol_id)
    if strategy_id:
        query = query.filter(TradeFact.strategy_id == strategy_id)
    
    # Apply pagination
    results = query.offset(skip).limit(limit).all()
    
    # Convert to list of dictionaries
    trades = []
    for row in results:
        trade_dict = {
            "id": row.id,
            "timestamp": row.timestamp.isoformat() if row.timestamp else None,
            "quantity": row.quantity,
            "price": row.price,
            "total_value": row.total_value,
            "symbol": row.symbol,
            "asset_class": row.asset_class,
            "trader_name": row.trader_name,
            "strategy_name": row.strategy_name
        }
        trades.append(trade_dict)
    
    return trades

@app.get("/performance/{strategy_id}")
def get_strategy_performance(
    strategy_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    # Log the request
    print(f"Performance request for strategy_id={strategy_id}, days={days}")
    
    # Calculate the start date
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Check if strategy exists
    strategy = db.query(StrategyDimension).filter(StrategyDimension.id == strategy_id).first()
    if not strategy:
        print(f"Strategy with id {strategy_id} not found in database")
        raise HTTPException(status_code=404, detail=f"Strategy with id {strategy_id} not found")
    
    print(f"Found strategy: {strategy.name}")
    
    # Get trade data
    trades = db.query(
        TradeFact.timestamp,
        TradeFact.total_value
    ).filter(
        TradeFact.strategy_id == strategy_id,
        TradeFact.timestamp >= start_date,
        TradeFact.timestamp <= end_date
    ).order_by(
        TradeFact.timestamp
    ).all()
    
    print(f"Found {len(trades)} trades for this strategy")
    
    # If no trades, return empty array with an info message
    if not trades:
        return []
    
    # Convert to pandas DataFrame for easier handling
    df = pd.DataFrame([(t.timestamp.date(), t.total_value) for t in trades], columns=['date', 'daily_value'])
    
    # Group by date and sum values
    performance = df.groupby('date')['daily_value'].sum().reset_index()
    
    # Convert to list of dictionaries
    return [{"date": row.date.isoformat(), "daily_value": row.daily_value} for _, row in performance.iterrows()]

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)