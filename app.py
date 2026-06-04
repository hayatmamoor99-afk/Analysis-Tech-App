import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="AI Fintech Intelligence",
    page_icon="📈",
    layout="wide"
)

# -----------------------------
# STYLING
# -----------------------------

st.markdown("""
<style>

.stApp{
    background: linear-gradient(
        135deg,
        #0f172a,
        #111827,
        #1e293b
    );
}

.main-title{
    text-align:center;
    font-size:55px;
    font-weight:bold;
    color:white;
}

.sub-title{
    text-align:center;
    color:#94a3b8;
    font-size:18px;
}

div[data-testid="stMetric"]{
    background:#1e293b;
    padding:15px;
    border-radius:15px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------

st.markdown(
    "<p class='main-title'>🚀 AI Fintech Intelligence</p>",
    unsafe_allow_html=True
)

st.markdown(
    "<p class='sub-title'>Professional Stock Analysis Dashboard</p>",
    unsafe_allow_html=True
)

st.markdown("---")

# -----------------------------
# USER INPUT
# -----------------------------

ticker = st.text_input(
    "Enter Stock Symbol",
    "AAPL"
).upper()

# -----------------------------
# BUTTON
# -----------------------------

if st.button("Analyze Stock"):

    try:

        data = yf.download(
            ticker,
            period="1y",
            progress=False,
            auto_adjust=True
        )

        if data.empty:
            st.error("No data found.")
            st.stop()

        # Handle Yahoo Finance data safely

        close = data["Close"]

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        current_price = float(close.iloc[-1])

        # Simple trend analysis

        sma20 = close.rolling(20).mean()
        sma50 = close.rolling(50).mean()

        sma20_value = float(sma20.iloc[-1])
        sma50_value = float(sma50.iloc[-1])

        if sma20_value > sma50_value:
            signal = "BUY"
            signal_text = "Bullish Trend Detected"
        elif sma20_value < sma50_value:
            signal = "SELL"
            signal_text = "Bearish Trend Detected"
        else:
            signal = "HOLD"
            signal_text = "Neutral Trend"

        # -----------------------------
        # METRICS
        # -----------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Current Price",
                f"${current_price:.2f}"
            )

        with col2:
            st.metric(
                "20-Day MA",
                f"${sma20_value:.2f}"
            )

        with col3:
            st.metric(
                "Signal",
                signal
            )

        st.markdown("---")

        # -----------------------------
        # CHART
        # -----------------------------

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=close,
                name="Price"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=sma20,
                name="20-Day MA"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=sma50,
                name="50-Day MA"
            )
        )

        fig.update_layout(
            template="plotly_dark",
            height=700,
            title=f"{ticker} Market Analysis"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # -----------------------------
        # AI INSIGHT
        # -----------------------------

        st.subheader("🤖 AI Market Insight")

        st.info(signal_text)

        if signal == "BUY":

            st.success("""
Long Bias Detected

Suggested Strategy:
• Consider gradual accumulation
• Medium-term outlook appears positive
• Monitor market news before entry
""")

        elif signal == "SELL":

            st.error("""
Bearish Bias Detected

Suggested Strategy:
• Avoid aggressive buying
• Wait for confirmation
• Monitor support levels
""")

        else:

            st.warning("""
Neutral Market

Suggested Strategy:
• Wait for stronger confirmation
• Observe volume and news flow
""")

    except Exception as e:

        st.error(f"Application Error: {e}")
