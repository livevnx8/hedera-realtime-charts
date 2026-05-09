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
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from technical_indicators import TechnicalIndicators


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


def create_advanced_chart(symbol: str, indicators: list = None, chart_type: str = "Line"):
    """Create an advanced candlestick chart with indicators."""
    history = st.session_state.price_history[symbol]
    
    if len(history) < 2:
        return go.Figure()
    
    # Convert to DataFrame
    df = pd.DataFrame(history)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    
    # Get prices for indicators
    prices = df["price"].tolist()
    highs = df["price"].tolist()  # Use price as high for line chart
    lows = df["price"].tolist()   # Use price as low for line chart
    
    # Calculate indicators if requested
    if indicators is None:
        indicators = ["MA10", "MA30", "BB", "RSI", "MACD"]
    
    indicator_results = TechnicalIndicators.calculate_all_indicators(prices, highs, lows)
    
    # Create subplots based on indicators
    rows = 2
    if "RSI" in indicators or "MACD" in indicators:
        rows = 3
    
    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.5, 0.25, 0.25] if rows == 3 else [0.7, 0.3],
        subplot_titles=(f"{symbol} Price", "Volume", "Indicators") if rows == 3 else (f"{symbol} Price", "Volume")
    )
    
    # Price chart based on type
    if chart_type == "Line":
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=df["price"],
                mode="lines",
                name=symbol,
                line=dict(color="#00bfa5", width=2)
            ),
            row=1, col=1
        )
    elif chart_type == "Area":
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
    elif chart_type == "Candlestick":
        # Simulate OHLC from line data
        fig.add_trace(
            go.Candlestick(
                x=df["time"],
                open=df["price"].shift(1).fillna(df["price"]),
                high=df["price"],
                low=df["price"],
                close=df["price"],
                name=symbol,
                increasing_line_color="#00bfa5",
                decreasing_line_color="#ff6b6b"
            ),
            row=1, col=1
        )
    
    # Moving averages
    if "MA10" in indicators and len(df) >= 10:
        ema20 = indicator_results["EMA20"]
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=ema20.values,
                mode="lines",
                name="EMA20",
                line=dict(color="#ff6b6b", width=1, dash="dash")
            ),
            row=1, col=1
        )
    
    if "MA30" in indicators and len(df) >= 30:
        ema50 = indicator_results["EMA50"]
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=ema50.values,
                mode="lines",
                name="EMA50",
                line=dict(color="#ffd93d", width=1, dash="dash")
            ),
            row=1, col=1
        )
    
    # Bollinger Bands (if enough data)
    if "BB" in indicators and len(df) >= 20:
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
    
    # RSI indicator
    if "RSI" in indicators and rows == 3:
        rsi = indicator_results["RSI"]
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=rsi.values,
                mode="lines",
                name="RSI",
                line=dict(color="#9c27b0", width=1)
            ),
            row=3, col=1
        )
        # Add overbought/oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="rgba(255, 99, 132, 0.5)", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="rgba(75, 192, 192, 0.5)", row=3, col=1)
    
    # MACD indicator
    if "MACD" in indicators and rows == 3:
        macd = indicator_results["MACD"]
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=macd.values,
                mode="lines",
                name="MACD",
                line=dict(color="#ff9800", width=1)
            ),
            row=3, col=1
        )
        fig.add_hline(y=0, line_dash="dash", line_color="rgba(255, 255, 255, 0.3)", row=3, col=1)
    
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
    
    # Update axes
    fig.update_xaxes(
        title_text="Time",
        row=rows, col=1
    )
    fig.update_yaxes(
        title_text="Price (USDT)",
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Volume",
        row=2, col=1
    )
    if rows == 3:
        fig.update_yaxes(
            title_text="Indicator Value",
            row=3, col=1
        )
    
    # Add crosshair
    fig.update_layout(
        template="plotly_dark",
        height=800 if rows == 3 else 600,
        margin=dict(l=0, r=0, t=30, b=0),
        hovermode="x unified",
        xaxis_showspikes=True,
        yaxis_showspikes=True,
        spikedistance=-1,
        hoverdistance=200,
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
    
    # Connection status
    if st.sidebar.button("Connect WebSocket"):
        if not st.session_state.connected:
            asyncio.run(connect_websocket())
    
    st.sidebar.write(f"Status: {'✅ Connected' if st.session_state.connected else '❌ Disconnected'}")
    
    # Indicator selection
    st.sidebar.subheader("Technical Indicators")
    available_indicators = ["MA10", "MA30", "BB", "RSI", "MACD", "Stochastic", "ATR"]
    selected_indicators = st.sidebar.multiselect(
        "Select Indicators",
        available_indicators,
        default=["MA10", "MA30", "BB", "RSI", "MACD"]
    )
    
    # Chart type selection
    st.sidebar.subheader("Chart Settings")
    chart_type = st.sidebar.selectbox("Chart Type", ["Line", "Area", "Candlestick"])
    
    # Timeframe selection
    timeframe = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"])
    
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
            fig = create_advanced_chart(selected_symbol, selected_indicators, chart_type)
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
                
                # Show indicator signals
                if selected_indicators:
                    st.subheader("Indicator Signals")
                    prices = [h["price"] for h in history]
                    highs = prices
                    lows = prices
                    indicators = TechnicalIndicators.calculate_all_indicators(prices, highs, lows)
                    
                    for ind_name in selected_indicators:
                        if ind_name in indicators:
                            result = indicators[ind_name]
                            if result.signals:
                                latest_signal = result.signals[-1]
                                signal_color = "🟢" if latest_signal == "buy" else "🔴" if latest_signal == "sell" else "⚪"
                                st.write(f"{signal_color} {ind_name}: {latest_signal.upper()}")
    
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
