import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD

# PAGE CONFIG
st.set_page_config(
    page_title="AI Fintech Intelligence",
    page_icon="📈",
    layout="wide"
)

# CUSTOM CSS
st.markdown("""
<style>

.stApp{
background: linear-gradient(135deg,#0f172a,#111827,#1e293b);
color:white;
}

h1,h2,h3,h4{
color:white;
text-align:center;
}

div[data-testid="stMetric"]{
background-color:#1e293b;
padding:15px;
border-radius:15px;
box-shadow:0 0 15px rgba(0,0,0,0.3);
}

</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown("""
<h1>🚀 AI Fintech Intelligence Platform</h1>
<h4>Stock Analysis | Technical Indicators | AI Insights</h4>
""", unsafe_allow_html=True)

# INPUT
ticker = st.text_input(
    "Enter Stock Symbol",
    "AAPL"
)

# BUTTON
if st.button("Analyze Stock"):

    data = yf.download(
        ticker,
        period="1y"
    )

    close = data["Close"]

    # RSI
    rsi = RSIIndicator(close).rsi()

    # MACD
    macd = MACD(close)

    data["RSI"] = rsi
    data["MACD"] = macd.macd()

    latest_rsi = data["RSI"].iloc[-1]
    latest_macd = data["MACD"].iloc[-1]

    if latest_rsi < 30:
        signal = "BUY"

    elif latest_rsi > 70:
        signal = "SELL"

    else:
        signal = "HOLD"

    # METRICS
    col1,col2,col3 = st.columns(3)

    with col1:
        st.metric(
            "RSI",
            round(float(latest_rsi),2)
        )

    with col2:
        st.metric(
            "MACD",
            round(float(latest_macd),2)
        )

    with col3:
        st.metric(
            "Signal",
            signal
        )

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
        height=600,
        title=f"{ticker} Price Chart"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("AI Recommendation")

    if signal == "BUY":
        st.success(
            "Stock appears oversold. Consider researching long opportunities."
        )

    elif signal == "SELL":
        st.error(
            "Stock appears overbought. Consider caution."
        )

    else:
        st.warning(
            "No strong signal currently."
        )
