# Business Intelligence Visualization Tool for Algorithmic Trading

A comprehensive, open-source business intelligence visualization tool designed for algorithmic trading systems. This application transforms complex trading data into intuitive visualizations, enabling traders and analysts to make data-driven decisions.

## Features

- **Multi-Asset Class Analysis**: Support for equities, cryptocurrencies, and forex
- **Interactive Dashboards**: Dynamic charts and filters for data exploration
- **Strategy Performance Tracking**: Monitor and compare trading strategies
- **Multi-Dimensional Analysis**: Filter by symbol, strategy, time period, and asset class
- **Real Market Data Integration**: Uses real-world data from Yahoo Finance
- **Star Schema Data Model**: Optimized for analytical processing
![image](https://github.com/user-attachments/assets/d8e71c13-7d8f-4fd1-be8a-ec6dc4bd1f22)


##  Technology Stack

- **Backend**: FastAPI + Uvicorn
- **Frontend**: Streamlit + Plotly
- **Database**: SQLite with SQLAlchemy ORM
- **Data Processing**: Pandas + yfinance
- **Version Control**: Git

## Getting Started

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/your-username/trading-bi-tool.git
   cd trading-bi-tool
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv ProjectVenv
   # On Windows
   ProjectVenv\Scripts\activate
   # On macOS/Linux
   source ProjectVenv/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the FastAPI backend server
   ```bash
   python bi_tool_test.py
   ```

2. In a new terminal, start the Streamlit frontend
   ```bash
   streamlit run bi_tool_streamlit.py
   ```

3. Load sample data (if needed)
   ```bash
   python load_market_data.py
   ```

4. Access the dashboard at http://localhost:8501

## Project Structure

```
Project/
├── Backend/
│   ├── __init__.py
│   ├── database.py      # Database models and connection
│   ├── etl.py           # ETL processes
│   ├── main.py          # API entry point
│   ├── models.py        # Data models
│   ├── routes.py        # API routes
│   └── services.py      # Business logic
│
├── Frontend/
│   ├── __init__.py
│   ├── app.py           # Streamlit application
│   ├── charts.py        # Chart definitions
│   └── data_loader.py   # API integration
│
├── ProjectVenv/         # Virtual environment
├── bi_tool_streamlit.py # Streamlit dashboard
├── bi_tool_test.py      # FastAPI server
├── database.py          # Main database models
├── load_market_data.py  # Data loading script
├── data.db              # SQLite database
└── README.md            # Project documentation
```

## Core Components

### 1. Data Model

The system implements a star schema with:
- **Fact Table**: trade_facts
- **Dimension Tables**: symbol_dim, trader_dim, strategy_dim

This design enables efficient querying and analysis across multiple dimensions.

### 2. API Endpoints

- `/symbols` - List all trading symbols
- `/strategies` - List all trading strategies
- `/traders` - List all traders
- `/trades` - Get trade data with optional filtering
- `/performance/{strategy_id}` - Get performance data for a strategy

### 3. Dashboard Visualizations

- Trading value by symbol
- Trading distribution by strategy
- Performance over time
- Recent trades table
- Key performance metrics

![image](https://github.com/user-attachments/assets/de645566-c837-407b-836f-e766c6e3749d)

![image](https://github.com/user-attachments/assets/c352de1d-7a62-4396-abb1-5b854dcfb707)

![image](https://github.com/user-attachments/assets/62144b42-8b59-4e71-ba40-8ba2327314e2)




## Contributors

- **Diego Mckay** - Initial project setup, database foundation, API framework, basic dashboard
- **Shefreen Kaur** - Advanced data modeling, data pipeline, enhanced API layer, advanced visualizations, system integration

## Academic Context

This project was developed as part of the COMP 430 course. It demonstrates the application of business intelligence principles, data visualization techniques, and full-stack development in the context of algorithmic trading systems.

## Future Enhancements

- Real-time data streaming via WebSockets
- User authentication and multitenancy
- Strategy backtesting capabilities
- Machine learning integration for predictive analytics
- Export capabilities for reports and analysis
