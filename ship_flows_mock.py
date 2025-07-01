import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import os

# --- Data Loading ---
@st.cache_data
 def load_ports(csv_path="ports.csv"):
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        # fallback to mock data
        df = pd.DataFrame([
            {"name": "Houston", "lat": 29.7522, "lon": -95.3584},
            {"name": "Rotterdam", "lat": 51.9244, "lon": 4.4777},
            {"name": "Singapore", "lat": 1.3521, "lon": 103.8198},
            {"name": "Ras Tanura", "lat": 26.6401, "lon": 50.1583},
            {"name": "Fujairah", "lat": 25.1288, "lon": 56.3265},
        ])
    return df

@st.cache_data
 def load_ships(csv_path="ships.csv"):
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame([
            {"name": "Crude Titan", "from": "Houston", "to": "Rotterdam", "progress": 0.3, "volume": 2.1},
            {"name": "Sea Giant", "from": "Ras Tanura", "to": "Singapore", "progress": 0.7, "volume": 1.8},
            {"name": "Ocean Star", "from": "Fujairah", "to": "Rotterdam", "progress": 0.5, "volume": 1.2},
            {"name": "Black Pearl", "from": "Houston", "to": "Singapore", "progress": 0.6, "volume": 2.5},
        ])
    return df

ports_df = load_ports()
ships_df = load_ships()

# Helper function with error handling
def get_port_df(df, name):
    row = df[df["name"] == name]
    if row.empty:
        st.warning(f"Port '{name}' not found in data.")
        return None
    return row.iloc[0]

# Calculate ship positions along great-circle-ish route (linear interpolation)
def compute_positions(ports, ships):
    positions = []
    flows = []
    max_vol = ships["volume"].max()
    for _, ship in ships.iterrows():
        start = get_port_df(ports, ship["from"])
        end = get_port_df(ports, ship["to"])
        if start is None or end is None:
            continue
        lat = start["lat"] + (end["lat"] - start["lat"]) * ship["progress"]
        lon = start["lon"] + (end["lon"] - start["lon"]) * ship["progress"]
        width = (ship["volume"] / max_vol) * 50  # normalize
        positions.append({
            "name": ship["name"],
            "lat": lat,
            "lon": lon,
            "from": ship["from"],
            "to": ship["to"],
            "volume": ship["volume"],
            "width": width,
        })
        flows.append({
            "from_lat": start["lat"],
            "from_lon": start["lon"],
            "to_lat": end["lat"],
            "to_lon": end["lon"],
            "volume": ship["volume"],
            "width": width,
            "name": ship["name"],
        })
    return pd.DataFrame(positions), pd.DataFrame(flows)

ships_pos_df, flows_df = compute_positions(ports_df, ships_df)

# --- Streamlit Layout ---
st.set_page_config(page_title="Crude Ship Flows Dashboard", layout="wide")
st.title("🛳️ Crude Oil Ship Flows")
st.markdown("""
This interactive map shows simulated crude oil tanker movements between major ports.
Use the controls to filter and explore the data. Data can be updated via CSV files in the app folder.
""")

# Sidebar controls
st.sidebar.header("Controls")
# Port filter
distinct_ports = ports_df["name"].tolist()
selected_port = st.sidebar.selectbox("Filter by origin port", ["All"] + distinct_ports)
# Volume range
min_vol, max_vol = float(ships_df["volume"].min()), float(ships_df["volume"].max())
vol_range = st.sidebar.slider("Volume (M bbl)", min_vol, max_vol, (min_vol, max_vol))
# Layer toggles
show_ports = st.sidebar.checkbox("Show Ports", value=True)
show_ships = st.sidebar.checkbox("Show Ships", value=True)
show_flows = st.sidebar.checkbox("Show Flows", value=True)

# Apply filters
filtered_ships = ships_pos_df[
    (ships_pos_df["volume"] >= vol_range[0]) &
    (ships_pos_df["volume"] <= vol_range[1])
]
if selected_port != "All":
    filtered_ships = filtered_ships[filtered_ships["from"] == selected_port]
filtered_flows = flows_df[flows_df["name"].isin(filtered_ships["name"])]

# Pydeck Layers
layers = []
if show_ports:
    port_layer = pdk.Layer(
        "ScatterplotLayer",
        data=ports_df,
        get_position='[lon, lat]',
        get_radius=50000,
        get_fill_color=[0, 0, 200, 180],
        pickable=True,
        tooltip="Port: {name}"
    )
    layers.append(port_layer)
if show_ships:
    ship_layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_ships,
        get_position='[lon, lat]',
        get_radius=filtered_ships["volume"] / max_vol * 200000,
        get_fill_color=[200, 0, 0, 180],
        pickable=True,
        tooltip="Ship: {name}\nVolume: {volume} M bbl"
    )
    layers.append(ship_layer)
if show_flows:
    flow_layer = pdk.Layer(
        "ArcLayer",
        data=filtered_flows,
        get_source_position='[from_lon, from_lat]',
        get_target_position='[to_lon, to_lat]',
        get_width="width",
        get_tilt=15,
        get_source_color=[0, 200, 0, 120],
        get_target_color=[200, 200, 0, 120],
        pickable=True,
        auto_highlight=True,
        tooltip="Route: {name}\nFrom: {from}\nTo: {to}\nVolume: {volume} M bbl"
    )
    layers.append(flow_layer)

# Initial viewstate
town_center = pdk.ViewState(latitude=30, longitude=0, zoom=2.2, pitch=0)

# Render map
if layers:
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=town_center,
        layers=layers
    ))
else:
    st.info("Enable at least one layer in the sidebar to display the map.")

# Data export
with st.expander("Download Data"):
    st.download_button("Download Ports", ports_df.to_csv(index=False), file_name="ports.csv")
    st.download_button("Download Ships", ships_df.to_csv(index=False), file_name="ships.csv")
    st.download_button("Download Flows", flows_df.to_csv(index=False), file_name="flows.csv")

# Optional raw tables
with st.expander("Show Raw Data Tables"):
    st.subheader("Ports")
    st.dataframe(ports_df)
    st.subheader("Ships (Filtered)")
    st.dataframe(filtered_ships)
    st.subheader("Flows (Filtered)")
    st.dataframe(filtered_flows)
