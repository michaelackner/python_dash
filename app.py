import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import json
import os
from typing import Dict, Optional, Tuple

# Page configuration
st.set_page_config(
    page_title="Oil Price Dashboard",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .price-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .price-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .price-change {
        font-size: 1.2rem;
        margin: 0.5rem 0;
    }
    .positive { color: #00ff88; }
    .negative { color: #ff6b6b; }
    .neutral { color: #ffffff; }
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
COMMODITIES_API_BASE_URL = "https://api.commodities-api.com/v1/latest"
CACHE_DURATION = 60  # seconds

@st.cache_data(ttl=CACHE_DURATION)
def fetch_oil_prices(api_key: str) -> Dict:
    """
    Fetch WTI and Brent oil prices from Commodities-API
    """
    try:
        # Fetch WTI (West Texas Intermediate)
        wti_params = {
            'access_key': api_key,
            'base': 'USD',
            'symbols': 'WTI'
        }
        
        # Fetch Brent
        brent_params = {
            'access_key': api_key,
            'base': 'USD',
            'symbols': 'BRENT'
        }
        
        # Make API calls
        wti_response = requests.get(COMMODITIES_API_BASE_URL, params=wti_params, timeout=10)
        brent_response = requests.get(COMMODITIES_API_BASE_URL, params=brent_params, timeout=10)
        
        if wti_response.status_code == 200 and brent_response.status_code == 200:
            wti_data = wti_response.json()
            brent_data = brent_response.json()
            
            return {
                'wti': {
                    'price': wti_data.get('data', {}).get('rates', {}).get('WTI', 0),
                    'timestamp': wti_data.get('data', {}).get('timestamp', 0),
                    'success': True
                },
                'brent': {
                    'price': brent_data.get('data', {}).get('rates', {}).get('BRENT', 0),
                    'timestamp': brent_data.get('data', {}).get('timestamp', 0),
                    'success': True
                }
            }
        else:
            st.error(f"API Error: WTI Status: {wti_response.status_code}, Brent Status: {brent_response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Network Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected Error: {str(e)}")
        return None

def format_price(price: float) -> str:
    """Format price with 2 decimal places"""
    return f"${price:.2f}"

def get_price_change_color(change: float) -> str:
    """Get color class based on price change"""
    if change > 0:
        return "positive"
    elif change < 0:
        return "negative"
    return "neutral"

def create_price_chart(price_history: Dict) -> go.Figure:
    """Create an interactive price chart using Plotly"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('WTI Crude Oil Price', 'Brent Crude Oil Price'),
        vertical_spacing=0.1,
        shared_xaxes=True
    )
    
    # WTI Chart
    if 'wti' in price_history and price_history['wti']:
        wti_times = [entry['timestamp'] for entry in price_history['wti']]
        wti_prices = [entry['price'] for entry in price_history['wti']]
        
        fig.add_trace(
            go.Scatter(
                x=wti_times,
                y=wti_prices,
                mode='lines+markers',
                name='WTI',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=6)
            ),
            row=1, col=1
        )
    
    # Brent Chart
    if 'brent' in price_history and price_history['brent']:
        brent_times = [entry['timestamp'] for entry in price_history['brent']]
        brent_prices = [entry['price'] for entry in price_history['brent']]
        
        fig.add_trace(
            go.Scatter(
                x=brent_times,
                y=brent_prices,
                mode='lines+markers',
                name='Brent',
                line=dict(color='#ff7f0e', width=3),
                marker=dict(size=6)
            ),
            row=2, col=1
        )
    
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="Oil Price Trends",
        title_x=0.5,
        font=dict(size=12)
    )
    
    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Price (USD)", row=2, col=1)
    
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">🛢️ Oil Price Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Commodities-API Key",
            type="password",
            help="Enter your Commodities-API access key"
        )
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto-refresh every 60s", value=True)
        
        # Manual refresh button
        if st.button("🔄 Refresh Now"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 About")
        st.markdown("""
        This dashboard fetches real-time oil prices:
        - **WTI**: West Texas Intermediate
        - **Brent**: Brent Crude Oil
        
        Data updates every 60 seconds.
        """)
        
        st.markdown("### 🔗 API Info")
        st.markdown("""
        Powered by [Commodities-API](https://commodities-api.com/)
        
        Get your free API key at:
        https://commodities-api.com/
        """)
    
    # Main content
    if not api_key:
        st.warning("⚠️ Please enter your Commodities-API key in the sidebar to start fetching data.")
        st.info("💡 Don't have an API key? Get a free one at https://commodities-api.com/")
        return
    
    # Initialize session state for price history
    if 'price_history' not in st.session_state:
        st.session_state.price_history = {'wti': [], 'brent': []}
    
    # Fetch current prices
    with st.spinner("🔄 Fetching latest oil prices..."):
        current_prices = fetch_oil_prices(api_key)
    
    if current_prices:
        # Update price history
        current_time = datetime.now()
        
        if current_prices['wti']['success']:
            st.session_state.price_history['wti'].append({
                'price': current_prices['wti']['price'],
                'timestamp': current_time
            })
        
        if current_prices['brent']['success']:
            st.session_state.price_history['brent'].append({
                'price': current_prices['brent']['price'],
                'timestamp': current_time
            })
        
        # Keep only last 100 entries to prevent memory issues
        if len(st.session_state.price_history['wti']) > 100:
            st.session_state.price_history['wti'] = st.session_state.price_history['wti'][-100:]
        if len(st.session_state.price_history['brent']) > 100:
            st.session_state.price_history['brent'] = st.session_state.price_history['brent'][-100:]
        
        # Display current prices
        col1, col2 = st.columns(2)
        
        with col1:
            if current_prices['wti']['success']:
                wti_price = current_prices['wti']['price']
                st.markdown(f"""
                <div class="price-card">
                    <h3>WTI Crude Oil</h3>
                    <div class="price-value">{format_price(wti_price)}</div>
                    <div class="price-change">West Texas Intermediate</div>
                    <div class="metric-card">
                        <strong>Last Updated:</strong><br>
                        {current_time.strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Failed to fetch WTI price")
        
        with col2:
            if current_prices['brent']['success']:
                brent_price = current_prices['brent']['price']
                st.markdown(f"""
                <div class="price-card">
                    <h3>Brent Crude Oil</h3>
                    <div class="price-value">{format_price(brent_price)}</div>
                    <div class="price-change">Brent Crude</div>
                    <div class="metric-card">
                        <strong>Last Updated:</strong><br>
                        {current_time.strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Failed to fetch Brent price")
        
        # Calculate spread
        if current_prices['wti']['success'] and current_prices['brent']['success']:
            spread = current_prices['brent']['price'] - current_prices['wti']['price']
            st.markdown("---")
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.1); border-radius: 10px;">
                <h3>📊 Brent-WTI Spread</h3>
                <div style="font-size: 2rem; font-weight: bold; color: {'#00ff88' if spread > 0 else '#ff6b6b'};">
                    {format_price(spread)}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Price history chart
        if len(st.session_state.price_history['wti']) > 1 or len(st.session_state.price_history['brent']) > 1:
            st.markdown("---")
            st.subheader("📈 Price History")
            chart = create_price_chart(st.session_state.price_history)
            st.plotly_chart(chart, use_container_width=True)
        
        # Recent price history table
        if st.session_state.price_history['wti'] or st.session_state.price_history['brent']:
            st.markdown("---")
            st.subheader("📋 Recent Price History")
            
            # Create DataFrame for display
            history_data = []
            max_length = max(len(st.session_state.price_history['wti']), len(st.session_state.price_history['brent']))
            
            for i in range(max_length):
                row = {'Timestamp': ''}
                if i < len(st.session_state.price_history['wti']):
                    row['WTI Price'] = format_price(st.session_state.price_history['wti'][i]['price'])
                    row['Timestamp'] = st.session_state.price_history['wti'][i]['timestamp'].strftime('%H:%M:%S')
                if i < len(st.session_state.price_history['brent']):
                    row['Brent Price'] = format_price(st.session_state.price_history['brent'][i]['price'])
                    if not row['Timestamp']:
                        row['Timestamp'] = st.session_state.price_history['brent'][i]['timestamp'].strftime('%H:%M:%S')
                history_data.append(row)
            
            if history_data:
                df = pd.DataFrame(history_data)
                st.dataframe(df, use_container_width=True)
    
    else:
        st.error("❌ Failed to fetch oil prices. Please check your API key and internet connection.")
    
    # Auto-refresh functionality
    if auto_refresh:
        time.sleep(60)
        st.rerun()

if __name__ == "__main__":
    main() 