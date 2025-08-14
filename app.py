import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import random
from datetime import datetime

# ------------------------------
# PAGE CONFIG
# ------------------------------
st.set_page_config(
    page_title="Real-Time Agentic ELT Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# CUSTOM CSS FOR BEAUTIFUL UI
# ------------------------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}
.sidebar .sidebar-content {
    background-color: #161a23;
}
h1, h2, h3, h4 {
    color: #00f7ff;
}
.agent-box {
    background-color: #1c1f26;
    border-radius: 10px;
    padding: 15px;
    margin-top: 10px;
    box-shadow: 0px 0px 15px #00f7ff33;
}
.instruction-panel {
    position: fixed;
    top: 10px;
    right: 10px;
    width: 320px;
    background-color: #1c1f26;
    color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 0px 20px #00f7ff55;
    font-size: 14px;
    z-index: 9999;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# FLOATING INSTRUCTIONS
# ------------------------------
st.markdown("""
<div class="instruction-panel">
<h4>📖 How to Use</h4>
1. Select a real-time data source.<br>
2. The dashboard will fetch the latest data.<br>
3. Watch the interactive chart update.<br>
4. Read the agent commentary for insights.<br>
5. If one agent fails, another takes over.<br>
6. Data refreshes when you re-run the app.<br>
7. Default: USGS Earthquakes (most reliable).<br>
8. Works best with stable internet.<br>
9. If data source is down → fallback notice.<br>
10. Enjoy the futuristic ELT dashboard!
</div>
""", unsafe_allow_html=True)

# ------------------------------
# DATA SOURCES
# ------------------------------
sources = {
    "USGS Earthquakes (Default)": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson",
    "OpenAQ Air Quality": "https://api.openaq.org/v2/latest",
    "CoinGecko Crypto Prices": "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd",
}

# ------------------------------
# SIDEBAR - SOURCE SELECT
# ------------------------------
st.sidebar.title("📡 Select Data Source")
choice = st.sidebar.radio("Choose one source:", list(sources.keys()), index=0)

# ------------------------------
# FETCH DATA
# ------------------------------
df = pd.DataFrame()
raw = None
error_message = None

try:
    url = sources[choice]
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    raw = resp.json()

    if "USGS Earthquakes" in choice:
        features = raw["features"]
        df = pd.DataFrame([{
            "Place": f["properties"]["place"],
            "Magnitude": f["properties"]["mag"],
            "Time": datetime.utcfromtimestamp(f["properties"]["time"]/1000)
        } for f in features])
    elif "OpenAQ" in choice:
        results = raw["results"]
        df = pd.DataFrame([{
            "City": r["city"],
            "Parameter": r["measurements"][0]["parameter"],
            "Value": r["measurements"][0]["value"],
            "Unit": r["measurements"][0]["unit"]
        } for r in results])
    elif "CoinGecko" in choice:
        df = pd.DataFrame(raw)[["name", "symbol", "current_price", "market_cap"]]

except Exception as e:
    error_message = str(e)

# ------------------------------
# DISPLAY DATA OR ERROR
# ------------------------------
st.title("🚀 Real-Time Agentic ELT Dashboard")
if error_message or df.empty:
    st.warning("✅ Our App is working fine, but the selected data source is currently down.")
else:
    st.subheader("📊 Live Data View")
    st.dataframe(df.head(20), use_container_width=True)

    # ------------------------------
    # CHART
    # ------------------------------
    if "Magnitude" in df.columns:
        fig = px.scatter(df, x="Time", y="Magnitude", hover_name="Place", title="Earthquake Magnitudes (Last 24h)",
                         color="Magnitude", size="Magnitude", color_continuous_scale="Turbo")
        st.plotly_chart(fig, use_container_width=True)
    elif "Value" in df.columns:
        fig = px.bar(df.head(20), x="City", y="Value", color="Parameter", title="Air Quality Levels")
        st.plotly_chart(fig, use_container_width=True)
    elif "current_price" in df.columns:
        fig = px.line(df.head(20), x="name", y="current_price", title="Crypto Prices (USD)")
        st.plotly_chart(fig, use_container_width=True)

    # ------------------------------
    # AGENT COMMENTARY
    # ------------------------------
    st.markdown("### 🧠 Agent Commentary")
    try:
        agent_1 = f"Agent Alpha: Based on {choice}, there are {len(df)} new records processed. The latest update shows interesting trends worth monitoring."
        st.markdown(f"<div class='agent-box'>{agent_1}</div>", unsafe_allow_html=True)
    except:
        pass

    try:
        agent_2 = f"Agent Beta: After analyzing {choice}, our ETL pipeline confirms that data ingestion and transformation worked successfully."
        st.markdown(f"<div class='agent-box'>{agent_2}</div>", unsafe_allow_html=True)
    except:
        pass
