"""Streamlit frontend for real-time crypto charts."""

import streamlit as st
import plotly.graph_objects as go
import asyncio
import websockets
import json
import time
from collections import defaultdict, deque
import pandas as pd


# Streamlit configuration
st.set_page_config(
    page_title="Hedera Realtime Charts",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "price_history" not in st.session_state:
    st.session_state.price_history = defaultdict(lambda: deque(maxlen=100))
if "connected" not in st.session_state:
    st.session_state.connected = False


async def connect_websocket():
    """Connect to the WebSocket server."""
    uri = "ws://localhost:8000/ws"
    try:
        async with websockets.connect(uri) as websocket:
            st.session_state.connected = True
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                if "type" in data and data["type"] == "init":
                    # Initialize with historical data
                    for symbol, price_info in data["data"].items():
                        st.session_state.price_history[symbol].append({
                            "time": time.time(),
                            "price": price_info["price"],
                        })
                else:
                    # Update with new price
                    symbol = data["symbol"]
                    st.session_state.price_history[symbol].append({
                        "time": time.time(),
                        "price": data["price"],
                    })
    except Exception as e:
        st.session_state.connected = False
        st.error(f"WebSocket connection error: {e}")


def create_chart(symbol: str):
    """Create a line chart for a symbol."""
    history = st.session_state.price_history[symbol]
    
    if not history:
        return go.Figure()
    
    df = pd.DataFrame(history)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["price"],
        mode="lines",
        name=symbol,
        line=dict(color="#00bfa5", width=2),
    ))
    
    fig.update_layout(
        title=f"{symbol} Price",
        xaxis_title="Time",
        yaxis_title="Price (USDT)",
        template="plotly_dark",
        height=400,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    
    return fig


def main():
    """Main Streamlit app."""
    st.title("📊 Hedera Realtime Crypto Charts")
    
    # Sidebar
    st.sidebar.header("Controls")
    
    if st.sidebar.button("Connect WebSocket"):
        if not st.session_state.connected:
            asyncio.run(connect_websocket())
    
    st.sidebar.write(f"Status: {'✅ Connected' if st.session_state.connected else '❌ Disconnected'}")
    
    # Symbol selection
    symbols = list(st.session_state.price_history.keys())
    if symbols:
        selected_symbol = st.sidebar.selectbox("Select Symbol", symbols)
    else:
        selected_symbol = None
        st.sidebar.write("No symbols available yet")
    
    # Main content
    if selected_symbol:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig = create_chart(selected_symbol)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Latest Price")
            history = st.session_state.price_history[selected_symbol]
            if history:
                latest = history[-1]
                st.metric("Price", f"${latest['price']:.4f}")
                st.metric("Update Time", time.strftime("%H:%M:%S", time.localtime(latest['time'])))
    
    # Show all symbols
    st.subheader("All Symbols")
    for symbol in symbols:
        with st.expander(symbol):
            fig = create_chart(symbol)
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
