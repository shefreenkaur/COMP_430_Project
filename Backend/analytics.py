# analytics.py
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from database import TradeFact, SymbolDimension, TraderDimension, StrategyDimension
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

def calculate_trading_metrics(db: Session, strategy_id: Optional[int] = None, 
                             symbol_id: Optional[int] = None, days: int = 30) -> Dict[str, Any]:
    """Calculate key trading metrics"""
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Build query
    query = db.query(TradeFact)
    
    # Apply filters
    query = query.filter(TradeFact.timestamp >= start_date)
    
    if strategy_id:
        query = query.filter(TradeFact.strategy_id == strategy_id)
        
    if symbol_id:
        query = query.filter(TradeFact.symbol_id == symbol_id)
    
    # Execute query
    trades = query.all()
    
    # If no trades, return empty metrics
    if not trades:
        return {
            "trade_count": 0,
            "total_value": 0,
            "avg_trade_size": 0,
            "metrics_period_days": days
        }
    
    # Calculate metrics
    trade_count = len(trades)
    total_value = sum(trade.total_value for trade in trades)
    avg_trade_size = total_value / trade_count if trade_count > 0 else 0
    
    # Group trades by day for time series analysis
    trade_dates = {}
    for trade in trades:
        date_key = trade.timestamp.date()
        if date_key not in trade_dates:
            trade_dates[date_key] = []
        trade_dates[date_key].append(trade)
    
    # Daily metrics
    daily_values = []
    
    for date, date_trades in sorted(trade_dates.items()):
        daily_value = sum(trade.total_value for trade in date_trades)
        daily_values.append({
            "date": date.isoformat(),
            "value": daily_value,
            "trade_count": len(date_trades)
        })
    
    # Calculate volatility if we have enough data
    volatility = 0
    if len(daily_values) > 1:
        values = [day["value"] for day in daily_values]
        diffs = np.diff(values) / values[:-1]  # percentage changes
        volatility = np.std(diffs) * np.sqrt(252)  # annualized volatility
    
    return {
        "trade_count": trade_count,
        "total_value": total_value,
        "avg_trade_size": avg_trade_size,
        "volatility": volatility,
        "metrics_period_days": days,
        "daily_values": daily_values
    }

def analyze_strategy_performance(db: Session, strategy_id: int, days: int = 90) -> Dict[str, Any]:
    """Analyze performance of a specific strategy"""
    
    # Get the strategy
    strategy = db.query(StrategyDimension).filter(StrategyDimension.id == strategy_id).first()
    if not strategy:
        return {"error": "Strategy not found"}
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get all trades for this strategy in the date range
    trades = db.query(
        TradeFact.timestamp,
        TradeFact.total_value,
        SymbolDimension.symbol,
        SymbolDimension.asset_class
    ).join(
        SymbolDimension, TradeFact.symbol_id == SymbolDimension.id
    ).filter(
        TradeFact.strategy_id == strategy_id,
        TradeFact.timestamp >= start_date,
        TradeFact.timestamp <= end_date
    ).order_by(
        TradeFact.timestamp
    ).all()
    
    # Convert to DataFrame
    df = pd.DataFrame([(
        t.timestamp,
        t.timestamp.date(),
        t.total_value,
        t.symbol,
        t.asset_class
    ) for t in trades], columns=['timestamp', 'date', 'value', 'symbol', 'asset_class'])
    
    if df.empty:
        return {
            "strategy_name": strategy.name,
            "strategy_type": strategy.type,
            "risk_profile": strategy.risk_profile,
            "trade_count": 0,
            "performance_summary": {
                "total_value": 0,
                "daily_average": 0
            },
            "daily_performance": []
        }
    
    # Calculate daily performance
    daily_perf = df.groupby('date')['value'].sum().reset_index()
    
    # Convert to list of dicts
    daily_performance = [{
        "date": row.date.isoformat(),
        "value": row.value
    } for _, row in daily_perf.iterrows()]
    
    # Asset class breakdown
    asset_class_breakdown = df.groupby('asset_class')['value'].sum().reset_index()
    asset_class_breakdown = [{
        "asset_class": row.asset_class,
        "value": row.value,
        "percentage": (row.value / df['value'].sum()) * 100
    } for _, row in asset_class_breakdown.iterrows()]
    
    # Symbol breakdown
    symbol_breakdown = df.groupby('symbol')['value'].sum().reset_index()
    symbol_breakdown = symbol_breakdown.sort_values('value', ascending=False).head(10)
    symbol_breakdown = [{
        "symbol": row.symbol,
        "value": row.value,
        "percentage": (row.value / df['value'].sum()) * 100
    } for _, row in symbol_breakdown.iterrows()]
    
    # Performance summary
    performance_summary = {
        "total_value": df['value'].sum(),
        "daily_average": df['value'].sum() / daily_perf.shape[0] if daily_perf.shape[0] > 0 else 0,
        "trade_count": df.shape[0],
        "unique_symbols": df['symbol'].nunique()
    }
    
    return {
        "strategy_name": strategy.name,
        "strategy_type": strategy.type,
        "risk_profile": strategy.risk_profile,
        "trade_count": df.shape[0],
        "performance_summary": performance_summary,
        "asset_class_breakdown": asset_class_breakdown,
        "top_symbols": symbol_breakdown,
        "daily_performance": daily_performance
    }