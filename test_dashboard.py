import streamlit as st
import requests
import time
from datetime import datetime

# Page setup
st.set_page_config(page_title="Oil Price Test", page_icon="🛢️", layout="wide")

# Simple header
st.title("🛢️ Oil Price Dashboard - Test Version")

# Sidebar for API key
with st.sidebar:
    st.header("⚙️ Setup")
    api_key = st.text_input("Commodities-API Key", type="password")
    if st.button("🔄 Test API"):
        st.cache_data.clear()

# Main content
if not api_key:
    st.warning("⚠️ Enter your API key in the sidebar")
    st.info("💡 Get free API key at: https://commodities-api.com/")
else:
    # Test API call
    try:
        url = "https://api.commodities-api.com/v1/latest"
        params = {
            'access_key': api_key,
            'base': 'USD',
            'symbols': 'WTI,BRENT'
        }
        
        with st.spinner("🔄 Fetching oil prices..."):
            response = requests.get(url, params=params, timeout=10)
            
        if response.status_code == 200:
            data = response.json()
            rates = data.get('data', {}).get('rates', {})
            
            # Display prices
            col1, col2 = st.columns(2)
            
            with col1:
                wti_price = rates.get('WTI', 0)
                st.metric("WTI Crude Oil", f"${wti_price:.2f}")
                
            with col2:
                brent_price = rates.get('BRENT', 0)
                st.metric("Brent Crude Oil", f"${brent_price:.2f}")
            
            # Show spread
            if wti_price and brent_price:
                spread = brent_price - wti_price
                st.metric("Brent-WTI Spread", f"${spread:.2f}")
            
            # Show timestamp
            st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
        else:
            st.error(f"API Error: {response.status_code}")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Auto-refresh info
st.markdown("---")
st.info("💡 This is a test version. The full dashboard includes charts, history, and auto-refresh.") 