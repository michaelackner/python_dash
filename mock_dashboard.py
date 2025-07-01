import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Page setup
st.set_page_config(page_title="Oil Price Mock", page_icon="🛢️", layout="wide")

# Simple header
st.title("🛢️ Oil Price Dashboard - Mock Version")

# Sidebar
with st.sidebar:
    st.header("⚙️ Mock Data")
    st.info("This is a demo with mock data")
    if st.button("🔄 Refresh Mock Data"):
        st.rerun()

# Generate mock data
def generate_mock_prices():
    base_wti = 75.50
    base_brent = 78.30
    
    # Add some random variation
    wti_price = base_wti + random.uniform(-2, 2)
    brent_price = base_brent + random.uniform(-2, 2)
    
    return wti_price, brent_price

# Generate mock historical data
def generate_mock_history():
    dates = []
    wti_prices = []
    brent_prices = []
    
    base_wti = 75.50
    base_brent = 78.30
    
    for i in range(24):  # Last 24 hours
        time_point = datetime.now() - timedelta(hours=23-i)
        dates.append(time_point)
        
        # Add realistic price movements
        wti_price = base_wti + random.uniform(-3, 3) + (i * 0.1)  # Slight trend
        brent_price = base_brent + random.uniform(-3, 3) + (i * 0.1)
        
        wti_prices.append(round(wti_price, 2))
        brent_prices.append(round(brent_price, 2))
    
    return dates, wti_prices, brent_prices

# Get current mock prices
wti_price, brent_price = generate_mock_prices()

# Display current prices
col1, col2 = st.columns(2)

with col1:
    st.metric(
        "WTI Crude Oil", 
        f"${wti_price:.2f}",
        delta=f"{random.uniform(-1, 1):.2f}"
    )
    
with col2:
    st.metric(
        "Brent Crude Oil", 
        f"${brent_price:.2f}",
        delta=f"{random.uniform(-1, 1):.2f}"
    )

# Show spread
spread = brent_price - wti_price
st.metric("Brent-WTI Spread", f"${spread:.2f}")

# Show timestamp
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Create mock chart
st.markdown("---")
st.subheader("📈 Mock Price History (Last 24 Hours)")

dates, wti_prices, brent_prices = generate_mock_history()

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=dates,
    y=wti_prices,
    mode='lines+markers',
    name='WTI',
    line=dict(color='#1f77b4', width=3),
    marker=dict(size=6)
))

fig.add_trace(go.Scatter(
    x=dates,
    y=brent_prices,
    mode='lines+markers',
    name='Brent',
    line=dict(color='#ff7f0e', width=3),
    marker=dict(size=6)
))

fig.update_layout(
    title="Oil Price Trends (Mock Data)",
    xaxis_title="Time",
    yaxis_title="Price (USD)",
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# Show mock data table
st.markdown("---")
st.subheader("📋 Recent Mock Data")

df = pd.DataFrame({
    'Time': [d.strftime('%H:%M') for d in dates[-10:]],  # Last 10 entries
    'WTI Price': [f"${p:.2f}" for p in wti_prices[-10:]],
    'Brent Price': [f"${p:.2f}" for p in brent_prices[-10:]],
    'Spread': [f"${b-p:.2f}" for p, b in zip(wti_prices[-10:], brent_prices[-10:])]
})

st.dataframe(df, use_container_width=True)

# Info about mock data
st.markdown("---")
st.info("""
💡 **Mock Data Info:**
- This is simulated data for testing purposes
- Prices are randomly generated around realistic values
- Use the full dashboard (`app.py`) with real API data for live prices
- Get a free API key at: https://commodities-api.com/

""") 