import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="AI Fintech Intelligence",
    page_icon="📈",
    layout="wide"
)

# -----------------------------------
# CUSTOM CSS
# -----------------------------------

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #0B0F19,
        #111827,
        #1E293B
    );
}

.main-title {
    text-align:center;
    color:white;
    font-size:50px;
    font-weight:bold;
}

.sub-title {
    text-align:center;
    color:#94A3B8;
    font-size:18px;
}

div[data-testid="stMetric"]{
    background-color:#1E293B;
    padding:15px;
    border-radius:15px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# HEADER
# -----------------------------------

st.markdown(
    '<p class="main-title">🚀 AI Fintech Intelligence Platform</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="sub-title">Stock Analysis • Market Signals • Interactive Charts</p>',
    unsafe_allow_html=True
)

st.markdown("---")

# -----------------------------------
# STOCK INPUT
# -----------------------------------

ticker = st.text_input(
    "Enter Stock Symbol",
    "AAPL"
).upper()

# -----------------------------------
# RSI FUNCTION
# -----------------------------------

def calculate_rsi(data, period=14):

    delta = data.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi

# -----------------------------------
# ANALYZE BUTTON
# -----------------------------------

if st.button("Analyze Stock"):

    with st.spinner("Analyzing Market Data..."):

        try:

            data = yf.download(
                ticker,
                period="1y",
                auto_adjust=True
            )

            if data.empty:
                st.error("No stock data found.")
                st.stop()

            close = data["Close"]

            data["RSI"] = calculate_rsi(close)

            latest_price = float(close.iloc[-1])
            latest_rsi = float(data["RSI"].iloc[-1])

            # SIGNAL

            if latest_rsi < 30:
                signal = "BUY"
                signal_color = "🟢"

            elif latest_rsi > 70:
                signal = "SELL"
                signal_color = "🔴"

            else:
                signal = "HOLD"
                signal_color = "🟡"

            # METRICS

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Current Price",
                    f"${latest_price:.2f}"
                )

            with col2:
                st.metric(
                    "RSI",
                    f"{latest_rsi:.2f}"
                )

            with col3:
                st.metric(
                    "Signal",
                    signal
                )

            st.markdown("---")

            # CHART

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["Close"],
                    mode="lines",
                    name="Price"
                )
            )

            fig.update_layout(
                template="plotly_dark",
                title=f"{ticker} Price Performance",
                height=650
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # AI SECTION

            st.subheader("🤖 AI Market Insight")

            if signal == "BUY":

                st.success(
                    f"""
                    RSI suggests {ticker} may be oversold.

                    Possible Opportunity:
                    - Direction: LONG
                    - Risk Level: Medium
                    - Strategy: Gradual Accumulation
                    """
                )

            elif signal == "SELL":

                st.error(
                    f"""
                    RSI suggests {ticker} may be overbought.

                    Possible Opportunity:
                    - Direction: SHORT / WAIT
                    - Risk Level: High
                    - Strategy: Avoid Chasing Price
                    """
                )

            else:

                st.warning(
                    f"""
                    No strong technical signal detected.

                    Possible Opportunity:
                    - Direction: HOLD
                    - Risk Level: Moderate
                    - Strategy: Wait For Confirmation
                    """
                )

        except Exception as e:

            st.error(f"Error: {e}")
