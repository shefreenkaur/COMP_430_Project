# In database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Existing SalesData model
class SalesData(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    product = Column(String, index=True)
    revenue = Column(Float)

# Trading data star schema
class TradeFact(Base):
    __tablename__ = 'trade_facts'
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    quantity = Column(Integer)
    price = Column(Float)
    total_value = Column(Float)
    
    # Foreign keys
    symbol_id = Column(Integer, ForeignKey('symbol_dim.id'))
    trader_id = Column(Integer, ForeignKey('trader_dim.id'))
    strategy_id = Column(Integer, ForeignKey('strategy_dim.id'))
    
    # Relationships
    symbol = relationship("SymbolDimension", back_populates="trades")
    trader = relationship("TraderDimension", back_populates="trades")
    strategy = relationship("StrategyDimension", back_populates="trades")

class SymbolDimension(Base):
    __tablename__ = 'symbol_dim'
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    asset_class = Column(String)
    sector = Column(String)
    
    # Back reference
    trades = relationship("TradeFact", back_populates="symbol")

class TraderDimension(Base):
    __tablename__ = 'trader_dim'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    team = Column(String)
    
    # Back reference
    trades = relationship("TradeFact", back_populates="trader")

class StrategyDimension(Base):
    __tablename__ = 'strategy_dim'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    risk_profile = Column(String)
    
    # Back reference
    trades = relationship("TradeFact", back_populates="strategy")

# Create all tables in the database
Base.metadata.create_all(bind=engine)