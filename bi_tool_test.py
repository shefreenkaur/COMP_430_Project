import os
import threading
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import subprocess
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import uvicorn
import sys
import time
# ----------------- DATABASE SETUP -----------------
DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class SalesData(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    product = Column(String, index=True)
    revenue = Column(Float)

Base.metadata.create_all(bind=engine)

# ----------------- ADD TEST DATA -----------------
def add_sample_data():
    db = SessionLocal()
    if db.query(SalesData).count() == 0:  # Avoid duplicate insertions
        sample_records = [
            SalesData(product="Laptop", revenue=5000.00),
            SalesData(product="Phone", revenue=3000.00),
            SalesData(product="Tablet", revenue=1500.00),
        ]
        db.add_all(sample_records)
        db.commit()
    db.close()

add_sample_data()  # Insert sample data on startup

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

@app.get("/sales")
def get_sales(db: Session = Depends(get_db)):
    data = db.query(SalesData).all()
    return [{"id": item.id, "product": item.product, "revenue": item.revenue} for item in data]

# ----------------- STREAMLIT FRONTEND -----------------
def run_streamlit():
    """Runs Streamlit as a separate process with the correct file path."""
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the current script directory
    streamlit_file = os.path.join(script_dir, "bi_tool_streamlit.py")  # Correct file path

    if not os.path.exists(streamlit_file):
        print(f"❌ ERROR: Streamlit file not found at {streamlit_file}")
        exit(1)
    else:
        print(f"✅ SUCCESS: Found Streamlit file at {streamlit_file}")

    subprocess.run(["streamlit", "run", streamlit_file], check=True)

# ----------------- RUN EVERYTHING -----------------
def run_fastapi():
    """Runs FastAPI server in a separate thread."""
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    if "streamlit" in sys.argv[0]:  
        # If Streamlit is running this script, do nothing
        exit(0)

    # Start FastAPI in a separate thread
    threading.Thread(target=run_fastapi, daemon=True).start()
  # Wait 3 seconds before starting Streamlit (so FastAPI is ready)
    time.sleep(3)
    # Run Streamlit separately
    run_streamlit()
