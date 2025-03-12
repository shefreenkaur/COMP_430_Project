import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.title("Business Intelligence Dashboard")

API_URL = "http://127.0.0.1:8000/sales"
response = requests.get(API_URL)

if response.status_code == 200:
    data = response.json()
    if data:
        df = pd.DataFrame(data)
        fig = px.bar(df, x="product", y="revenue", title="Sales Revenue")
        st.plotly_chart(fig)
    else:
        st.write("No data available. Add some records to the database.")
else:
    st.write("Error fetching data from API.")
