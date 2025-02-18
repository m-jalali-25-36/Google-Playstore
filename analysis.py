import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# API Base URL
API_URL = "http://localhost:8000"

# Fetch data from API
def fetch_data(category=None, min_rating=None, max_price=None, page=1, size=10):
    params = {"page": page, "size": size}
    if category:
        params["category"] = category
    if min_rating:
        params["min_rating"] = min_rating
    if max_price:
        params["max_price"] = max_price
    response = requests.get(f"{API_URL}/apps", params=params)
    return response.json()

# Sidebar filters
st.sidebar.header("Filters")
category = st.sidebar.text_input("Category")
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.1)
max_price = st.sidebar.number_input("Max Price", min_value=0.0, value=10.0)

# Pagination Controls
page = st.sidebar.number_input("Page", min_value=1, value=1)
size = st.sidebar.number_input("Page Size", min_value=1, max_value=100, value=10)

# Fetch Data
data = fetch_data(category, min_rating, max_price, page, size)
df = pd.DataFrame(data.get("apps", []))

# Display Table
st.write("### App List")
st.dataframe(df)

# Plot Rating Distribution
if not df.empty:
    fig = px.histogram(df, x="Rating", nbins=20, title="Rating Distribution")
    st.plotly_chart(fig)
    
    # Scatter Plot: Installs vs Price
    fig2 = px.scatter(df, x="Price", y="Installs", color="Category", title="Installs vs Price")
    st.plotly_chart(fig2)
else:
    st.warning("No data found with the given filters!")
