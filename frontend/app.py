"""Streamlit frontend for real-time crypto charts."""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import asyncio
import websockets
import json
import time
from collections import defaultdict, deque
import pandas as pd
import numpy as np


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


def create_advanced_chart(symbol: str):
    """Create an advanced candlestick chart with indicators."""
    history = st.session_state.price_history[symbol]
    
    if len(history) < 2:
        return go.Figure()
    
    # Convert to DataFrame
    df = pd.DataFrame(history)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=(f"{symbol} Price", "Volume")
    )
    
    # Price line with area fill
    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["price"],
            mode="lines",
            name=symbol,
            line=dict(color="#00bfa5", width=2),
            fill="tozeroy",
            fillcolor="rgba(0, 191, 165, 0.1)"
        ),
        row=1, col=1
    )
    
    # Moving averages
    if len(df) >= 10:
        df["MA10"] = df["price"].rolling(window=10).mean()
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=df["MA10"],
                mode="lines",
                name="MA10",
                line=dict(color="#ff6b6b", width=1, dash="dash")
            ),
            row=1, col=1
        )
    
    if len(df) >= 30:
        df["MA30"] = df["price"].rolling(window=30).mean()
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=df["MA30"],
                mode="lines",
                name="MA30",
                line=dict(color="#ffd93d", width=1, dash="dash")
            ),
            row=1, col=1
        )
    
    # Bollinger Bands (if enough data)
    if len(df) >= 20:
        df["BB_middle"] = df["price"].rolling(window=20).mean()
        df["BB_std"] = df["price"].rolling(window=20).std()
        df["BB_upper"] = df["BB_middle"] + (df["BB_std"] * 2)
        df["BB_lower"] = df["BB_middle"] - (df["BB_std"] * 2)
        
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=df["BB_upper"],
                mode="lines",
                name="BB Upper",
                line=dict(color="#6c757d", width=1),
                showlegend=False
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=df["BB_lower"],
                mode="lines",
                name="BB Lower",
                line=dict(color="#6c757d", width=1),
                fill="tonexty",
                fillcolor="rgba(108, 117, 125, 0.1)",
                showlegend=False
            ),
            row=1, col=1
        )
    
    # Volume bars
    colors = ["#00bfa5" if (i > 0 and df["price"].iloc[i] >= df["price"].iloc[i-1]) else "#ff6b6b" 
              for i in range(len(df))]
    
    fig.add_trace(
        go.Bar(
            x=df["time"],
            y=df.get("quantity", [1] * len(df)),
            name="Volume",
            marker_color=colors,
            opacity=0.6
        ),
        row=2, col=1
    )
    
    fig.update_xaxes(
        title_text="Time",
        row=2, col=1
    )
    fig.update_yaxes(
        title_text="Price (USDT)",
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Volume",
        row=2, col=1
    )
    fig.update_layout(
        template="plotly_dark",
        height=600,
        margin=dict(l=0, r=0, t=30, b=0),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def main():
    """Main Streamlit app."""
    st.title("📊 Hedera Realtime Crypto Charts - Top 50")
    
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
            fig = create_advanced_chart(selected_symbol)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Latest Price")
            history = st.session_state.price_history[selected_symbol]
            if history:
                latest = history[-1]
                st.metric("Price", f"${latest['price']:.4f}")
                st.metric("Update Time", time.strftime("%H:%M:%S", time.localtime(latest['time'])))
                
                # Calculate statistics
                prices = [h["price"] for h in history]
                if len(prices) >= 2:
                    change = prices[-1] - prices[0]
                    change_pct = (change / prices[0]) * 100
                    st.metric("Change", f"{change:+.4f}", f"{change_pct:+.2f}%")
                
                st.metric("Data Points", len(history))
    
    # Show all symbols (expandable)
    with st.expander("All Symbols"):
        if symbols:
            cols = st.columns(5)
            for i, symbol in enumerate(symbols):
                with cols[i % 5]:
                    st.metric(symbol, f"${st.session_state.price_history[symbol][-1]['price']:.4f}" 
                              if st.session_state.price_history[symbol] else "N/A")


if __name__ == "__main__":
    main()
