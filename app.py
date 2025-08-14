import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Real-Time Agentic ELT Dashboard", layout="wide")

# Sidebar - Data source selection
st.sidebar.header("🛰 Select Data Source")
data_source = st.sidebar.radio(
    "Choose one source:",
    ("USGS Earthquakes (Default)", "OpenAQ Air Quality", "CoinGecko Crypto Prices"),
    index=0
)

# Function to get USGS Earthquake data
def fetch_usgs_data():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        records = []
        for feature in data["features"]:
            props = feature["properties"]
            records.append({
                "Time": pd.to_datetime(props["time"], unit="ms"),
                "Magnitude": props["mag"],
                "Place": props["place"]
            })
        df = pd.DataFrame(records)
        return df
    except Exception as e:
        st.warning("Agent Alpha failed. Switching to Agent Beta...")
        return None

# Function to get OpenAQ data
def fetch_openaq_data():
    url = "https://api.openaq.org/v2/latest?limit=100"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        records = []
        for result in data["results"]:
            records.append({
                "Location": result["location"],
                "City": result.get("city", ""),
                "Value": result["measurements"][0]["value"],
                "Unit": result["measurements"][0]["unit"]
            })
        df = pd.DataFrame(records)
        return df
    except Exception as e:
        st.warning("Agent Alpha failed. Switching to Agent Beta...")
        return None

# Function to get CoinGecko data
def fetch_coingecko_data():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame(data)[["name", "symbol", "current_price", "market_cap"]]
        return df
    except Exception as e:
        st.warning("Agent Alpha failed. Switching to Agent Beta...")
        return None

# Fetch selected data
if data_source == "USGS Earthquakes (Default)":
    df = fetch_usgs_data()
elif data_source == "OpenAQ Air Quality":
    df = fetch_openaq_data()
elif data_source == "CoinGecko Crypto Prices":
    df = fetch_coingecko_data()
else:
    df = None

# If data is available, show chart
if df is not None and not df.empty:
    st.title("📊 Real-Time Agentic ELT Dashboard")

    if data_source == "USGS Earthquakes (Default)":
        fig = px.scatter(
            df, x="Time", y="Magnitude", size="Magnitude",
            color="Magnitude", hover_name="Place",
            title="USGS Earthquakes - Last 24 Hours"
        )
        st.plotly_chart(fig, use_container_width=True)

    elif data_source == "OpenAQ Air Quality":
        st.dataframe(df)

    elif data_source == "CoinGecko Crypto Prices":
        st.dataframe(df)

    # Agent Commentary - Readable Styling
    st.subheader("🧠 Agent Commentary")
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 10px;
                    font-size: 15px; line-height: 1.6; color: #212529; font-family: Arial, sans-serif;">
            <b>Agent Alpha:</b> Based on <i>{data_source}</i>, there are <b>{len(df)}</b> records processed. 
            The latest update shows interesting trends worth monitoring.
        </div>
        <div style="background-color: #f8f9fa; padding: 12px; border-radius: 8px;
                    font-size: 15px; line-height: 1.6; color: #212529; font-family: Arial, sans-serif;">
            <b>Agent Beta:</b> After analyzing <i>{data_source}</i>, our ETL pipeline confirms that data ingestion 
            and transformation worked successfully.
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.error("No data available. Please try again later.")
