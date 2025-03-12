from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import uvicorn
import pandas as pd

# Import your database models
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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)