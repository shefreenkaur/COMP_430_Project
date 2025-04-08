import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import json

# Set page config
st.set_page_config(
    page_title="Algorithmic Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for refresh handling
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0

# API base URL
API_URL = "http://127.0.0.1:8000"

# App title
st.title("Algorithmic Trading Dashboard")

# Functions to fetch data from API
def fetch_symbols():
    try:
        response = requests.get(f"{API_URL}/symbols")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching symbols: Status code {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching symbols: {e}")
        return []

def fetch_strategies():
    try:
        response = requests.get(f"{API_URL}/strategies")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching strategies: Status code {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching strategies: {e}")
        return []

def fetch_trades(params=None):
    try:
        # Debug info - can be removed later
        st.sidebar.expander("Debug Info").write(f"API params: {params}")
        
        response = requests.get(f"{API_URL}/trades", params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API returned error: {response.status_code}")
            # Display response text if available
            if hasattr(response, 'text'):
                st.error(f"Response: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error fetching trades: {e}")
        return []

def fetch_performance(strategy_id, days=30):
    try:
        response = requests.get(f"{API_URL}/performance/{strategy_id}?days={days}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching performance: Status code {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching performance: {e}")
        return []

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
today = datetime.now()
default_start = today - timedelta(days=30)
start_date = st.sidebar.date_input("Start Date", default_start)
end_date = st.sidebar.date_input("End Date", today)

# Fetch symbols and strategies for filters
symbols = fetch_symbols()
strategies = fetch_strategies()

# Symbol filter
symbol_options = ["All"] + [s["symbol"] for s in symbols]
selected_symbol = st.sidebar.selectbox("Symbol", symbol_options)

# Strategy filter
strategy_options = ["All"] + [s["name"] for s in strategies]
selected_strategy = st.sidebar.selectbox("Strategy", strategy_options)

# Asset class filter
asset_classes = ["All", "Equity", "Crypto", "Forex"]
selected_asset_class = st.sidebar.selectbox("Asset Class", asset_classes)

# Manual refresh button
if st.sidebar.button("Refresh Data"):
    st.session_state.refresh_count += 1

# Prepare filter parameters for API
params = {}

# Date filters - ensure proper formatting
if start_date:
    params["start_date"] = start_date.isoformat()
if end_date:
    # Add one day to include the end date in results
    end_date_adjusted = end_date + timedelta(days=1)
    params["end_date"] = end_date_adjusted.isoformat()

# Symbol filter
if selected_symbol != "All":
    # Find the ID of the selected symbol
    symbol_id = None
    for s in symbols:
        if s["symbol"] == selected_symbol:
            symbol_id = s["id"]
            break
    
    if symbol_id is not None:
        params["symbol_id"] = symbol_id

# Strategy filter
if selected_strategy != "All":
    # Find the ID of the selected strategy
    strategy_id = None
    for s in strategies:
        if s["name"] == selected_strategy:
            strategy_id = s["id"]
            break
    
    if strategy_id is not None:
        params["strategy_id"] = strategy_id

# Note: We'll handle asset class filtering in Streamlit after getting data
# because it's easier than modifying the API endpoint

# Fetch trading data
trades = fetch_trades(params)

# Process and display data
if not trades:
    st.warning("No trading data available. Make sure the API is running and data is loaded.")
else:
    # Convert to DataFrame
    df = pd.DataFrame(trades)
    
    # Apply asset class filter if needed
    if selected_asset_class != "All" and "asset_class" in df.columns:
        df = df[df["asset_class"] == selected_asset_class]
    
    # If dataframe is empty after filtering
    if df.empty:
        st.warning("No data matching your filters. Try adjusting your filter criteria.")
    else:
        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Dashboard metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Trades", f"{len(df):,}")
        
        with col2:
            total_value = df["total_value"].sum()
            st.metric("Total Value", f"${total_value:,.2f}")
        
        with col3:
            avg_price = df["price"].mean()
            st.metric("Avg Price", f"${avg_price:,.2f}")
        
        with col4:
            # Daily change calculation
            df["date"] = df["timestamp"].dt.date
            daily_totals = df.groupby("date")["total_value"].sum()
            if len(daily_totals) > 1:
                daily_change = (daily_totals.iloc[-1] / daily_totals.iloc[-2] - 1) * 100
                st.metric("Daily Change", f"{daily_change:.2f}%", delta=daily_change)
            else:
                st.metric("Daily Change", "N/A")
        
        # Trading by Symbol
        st.subheader("Trading by Symbol")
        symbol_data = df.groupby("symbol")["total_value"].sum().reset_index()
        symbol_data = symbol_data.sort_values("total_value", ascending=False)
        
        fig1 = px.bar(
            symbol_data,
            x="symbol",
            y="total_value",
            title="Total Value by Symbol",
            labels={"total_value": "Value ($)", "symbol": "Symbol"},
            width=800,  # Set explicit width
            text_auto=True      
        )
        fig1.update_layout(
            xaxis_title="Symbol",
            yaxis_title="Value ($)",
            bargap=0.4,  # Add space between bars
            yaxis=dict(
                tickformat=",.0f",  # Format numbers with commas
            )
        )
        # Use a unique key with refresh count to avoid duplicate key errors
        st.plotly_chart(fig1, use_container_width=True, key=f"symbol_chart_{st.session_state.refresh_count}")
        
        # Trading by Strategy and Performance/Time series charts
        col1, col2 = st.columns(2)
        
        with col1:
            strategy_data = df.groupby("strategy_name")["total_value"].sum().reset_index()
            
            fig2 = px.pie(
                strategy_data,
                values="total_value",
                names="strategy_name",
                title="Value by Strategy"
            )
            fig2.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig2, use_container_width=True, key=f"strategy_pie_{st.session_state.refresh_count}")
        
        with col2:
            # Performance chart logic
            if selected_strategy != "All" and 'strategy_id' in locals() and strategy_id is not None:
                perf_data = fetch_performance(strategy_id)
                if perf_data:
                    perf_df = pd.DataFrame(perf_data)
                    perf_df["date"] = pd.to_datetime(perf_df["date"])
                    
                    fig3 = px.line(
                        perf_df,
                        x="date",
                        y="daily_value",
                        title=f"{selected_strategy} Daily Performance",
                        labels={"daily_value": "Value ($)", "date": "Date"}
                    )
                    st.plotly_chart(fig3, use_container_width=True, key=f"perf_chart_{st.session_state.refresh_count}")
                else:
                    st.info("No performance data available for this strategy.")
            else:
                # Trading over time (all strategies)
                time_data = df.groupby("date")["total_value"].sum().reset_index()
                
                fig3 = px.line(
                    time_data,
                    x="date",
                    y="total_value",
                    title="Trading Value Over Time",
                    labels={"total_value": "Value ($)", "date": "Date"}
                )
                st.plotly_chart(fig3, use_container_width=True, key=f"time_series_{st.session_state.refresh_count}")
        
        # Recent trades table
        st.subheader("Recent Trades")
        recent_trades = df.sort_values("timestamp", ascending=False).head(10)
        recent_trades["timestamp"] = recent_trades["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
        
        display_cols = ["timestamp", "symbol", "quantity", "price", "total_value", "strategy_name", "trader_name"]
        display_cols = [col for col in display_cols if col in recent_trades.columns]
        
        st.dataframe(recent_trades[display_cols], use_container_width=True)