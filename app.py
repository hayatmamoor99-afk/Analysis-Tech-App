import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

st.set_page_config(
    page_title="FinSight AI",
    page_icon="📈",
    layout="wide"
)

st.title("📈 FinSight AI")
st.subheader("AI-Powered Stock Analysis Platform")

st.markdown("""
### Features

✅ Historical Performance

✅ Investment Growth

✅ Risk Analysis

✅ Probability Analysis

✅ AI Insights
""")

st.markdown("""
<style>

.main {background-color: #0B1220;}

.stApp {background-color: #0B1220;}

h1 {color: #FFD54F;}

h2,h3 {color: white;}

</style>, unsafe_allow_html=True)

ticker = st.text_input("Enter Stock Symbol", value="NVDA")
st.info("Enter any Yahoo Finance ticker symbol such as NVDA, TSLA, MSFT, PLTR, AAPL, GOOGL, AMZN, META, BTC-USD etc.")
ticker = ticker.upper()
try:

    stock = yf.Ticker(ticker)

    info = stock.info

    data = stock.history(period="5y")

    if data.empty:
        st.error("No data found.")
        st.stop()

except Exception:

    st.error("Invalid ticker.")
    st.stop()
info = stock.info
st.subheader(info.get("longName","Unknown"))

col1,col2,col3,col4 = st.columns(4)

col1.metric(
    "Current Price",
    f"${info.get('currentPrice','N/A')}"
)

col2.metric(
    "Market Cap",
    f"${round(info.get('marketCap',0)/1e9,2)}B"
)

col3.metric(
    "P/E Ratio",
    info.get("trailingPE","N/A")
)

col4.metric(
    "Sector",
    info.get("sector","N/A")
)
stock = yf.Ticker(ticker)    
import yfinance as yf
import pandas as pd

if ticker:

    stock = yf.Ticker(ticker)

    data = stock.history(period="5y")

    st.write(data.head())

    import plotly.express as px

    fig = px.line( data,
    x=data.index,
    y="Close",
    title=f"{ticker} Price History (5 Years)")

st.plotly_chart(fig,use_container_width=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1 Year",
    "2 Years",
    "3 Years",
    "4 Years",
    "5 Years"
])

with tab1:

    d1 = stock.history(period="1y")

    fig = px.line(
        d1,
        x=d1.index,
        y="Close",
        title=f"{ticker} - 1 Year"
    )

    st.plotly_chart(fig,
                     use_container_width=True)

    with tab2:

    d2 = stock.history(period="2y")

    fig = px.line(
        d2,
        x=d2.index,
        y="Close",
        title=f"{ticker} - 2 Year"
    )

    st.plotly_chart(fig,
                     use_container_width=True)

3y
4y
5y

returns = d1["Close"].pct_change().dropna()

fig_hist = px.histogram(
    returns,
    nbins=50,
    title="Return Distribution"
)

st.plotly_chart(fig_hist,
                use_container_width=True)

start_price = d1["Close"].iloc[0]

current_price = d1["Close"].iloc[-1]

investment_value = 100 * (current_price / start_price)

profit = investment_value - 100

st.metric(
    "Current Value of $100 Investment",
    f"${investment_value:.2f}",
    f"{profit:.2f}"
)

returns = data["Close"].pct_change().dropna()
volatility = returns.std() * (252 ** 0.5)
st.subheader("Risk Analysis")

st.metric(
    "Annual Volatility",
    f"{volatility*100:.2f}%"
)
if volatility < 0.20:

    risk = "LOW"

elif volatility < 0.40:

    risk = "MEDIUM"

else:

    risk = "HIGH"

st.metric(
    "Risk Level",
    risk
)
positive_days = len(
    returns[returns > 0]
)

total_days = len(returns)

probability_gain = (
    positive_days / total_days
) * 100
st.metric(
    "Probability of Gain",
    f"{probability_gain:.2f}%"
)
probability_loss = (
    100 - probability_gain
)

ma50 = data["Close"].rolling(
    50
).mean()

ma200 = data["Close"].rolling(
    200
).mean()

latest_ma50 = ma50.iloc[-1]

latest_ma200 = ma200.iloc[-1]

if latest_ma50 > latest_ma200:

    signal = "BUY"

elif probability_gain > 55:

    signal = "HOLD"

else:

    signal = "AVOID"

st.subheader(
    "AI Recommendation"
)

st.success(signal)

score = 0
if latest_ma50 > latest_ma200:
    score += 40
score += probability_gain * 0.4
if volatility < 0.25:
    score += 20
score = round(score)
st.metric(
    "Bullish Score",
    f"{score}/100"
)

st.info("""
80-100 : Strong Buy

60-80 : Buy

40-60 : Hold

20-40 : Weak

0-20 : Avoid
""")

import numpy as np
import plotly.graph_objects as go

returns = data["Close"].pct_change().dropna()

mu = returns.mean()

sigma = returns.std()

simulation_days = 252
simulation_count = 1000

current_price = data["Close"].iloc[-1]

simulations = np.zeros(
    (simulation_days,
     simulation_count)
)

for i in range(simulation_count):

    prices = [current_price]

    for day in range(simulation_days):

        next_price = prices[-1] * (
            1 +
            np.random.normal(mu,sigma)
        )

        prices.append(next_price)

    simulations[:,i] = prices[1:]

fig = go.Figure()

for i in range(100):

    fig.add_trace(
        go.Scatter(y=simulations[:,i], mode="lines", opacity=0.15, showlegend=False)
    )

fig.update_layout(
    title="Monte Carlo Forecast",
    xaxis_title="Future Trading Days",
    yaxis_title="Projected Price"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

final_prices = simulations[-1]

expected_price = np.mean(
    final_prices
)

best_case = np.percentile(
    final_prices,
    90
)

worst_case = np.percentile(
    final_prices,
    10
)

col1,col2,col3 = st.columns(3)

col1.metric(
    "Worst Case",
    f"${worst_case:.2f}"
)

col2.metric(
    "Expected Price",
    f"${expected_price:.2f}"
)

col3.metric(
    "Best Case",
    f"${best_case:.2f}"
)

lower = np.percentile(
    final_prices,
    2.5
)

upper = np.percentile(
    final_prices,
    97.5
)

st.info(
    f"""
95% Confidence Interval

${lower:.2f}
to
${upper:.2f}
"""
)

positive = (
    final_prices > current_price
).mean()

future_probability = (
    positive * 100
)

st.metric(
    "Probability of Higher Price in 1 Year",
    f"{future_probability:.2f}%"
)

if future_probability > 75:

    future_signal = "STRONG BUY"

elif future_probability > 60:

    future_signal = "BUY"

elif future_probability > 45:

    future_signal = "HOLD"

else:

    future_signal = "AVOID"

st.subheader(
    "Future Outlook"
)

st.success(
    future_signal
)

explanation = f"""

Current Price:
${current_price:.2f}

Expected Price:
${expected_price:.2f}

Probability of Gain:
{future_probability:.2f}%

Volatility:
{sigma*100:.2f}%

Recommendation:
{future_signal}
"""

st.text_area(
    "AI Explanation",
    explanation,
    height=250
)

np.random.normal()

info = stock.info

st.header("Company Overview")

st.write(
    info.get("longBusinessSummary",
             "No description available.")
)

col1,col2,col3,col4 = st.columns(4)

col1.metric(
    "Sector",
    info.get("sector","N/A")
)

col2.metric(
    "Industry",
    info.get("industry","N/A")
)

col3.metric(
    "Employees",
    info.get("fullTimeEmployees","N/A")
)

col4.metric(
    "Country",
    info.get("country","N/A")
)

pe = info.get("trailingPE")

pb = info.get("priceToBook")

roe = info.get("returnOnEquity")

profit_margin = info.get("profitMargins")

st.subheader(
    "Fundamental Analysis"
)

st.metric("P/E", pe)

st.metric("P/B", pb)

st.metric(
    "ROE",
    f"{roe*100:.2f}%"
)

st.metric(
    "Profit Margin",
    f"{profit_margin*100:.2f}%"
)

health_score = 50
if roe > 0.15:
    health_score += 15
if profit_margin > 0.10:
    health_score += 15
if pe and pe < 30:
    health_score += 20
st.metric(
    "Financial Health",
    f"{health_score}/100"
)
current_price
expected_price
upside = (
    expected_price-current_price
)/current_price *100
st.metric(
    "Potential Upside",
    f"{upside:.2f}%"
)
bull_case = f"""

Reasons to be Bullish

• Strong historical growth

• Positive trend

• Probability of gain:
{future_probability:.2f}%

• Expected future price:
${expected_price:.2f}

"""
st.success(
    bull_case
)
bear_case = f"""

Risks

• Market volatility

• Earnings miss

• Economic slowdown

• Competition pressure

"""
bear_case = f"""

Risks

• Market volatility

• Earnings miss

• Economic slowdown

• Competition pressure

"""

st.error(
    bear_case
)

with st.sidebar:

st.header(
    "Learning Center"
)
st.expander(
    "What is Volatility?"
)
Higher volatility means
larger price swings.

Higher reward potential.

Higher risk.
st.expander(
    "What is Probability of Gain?"
)
Historical percentage
of days where stock
closed higher.
st.expander(
    "What is Monte Carlo?"
)
A simulation technique
used by hedge funds
and investment banks
to estimate possible
future outcomes.
Bullish Score

Financial Health

Future Probability

analyst_score = (
    score*0.4
    +
    health_score*0.3
    +
    future_probability*0.3
)

st.metric(
    "Analyst Score",
    f"{analyst_score:.0f}/100"
)

if analyst_score > 80:

    verdict = "STRONG BUY"

elif analyst_score > 65:

    verdict = "BUY"

elif analyst_score > 50:

    verdict = "HOLD"

else:

    verdict = "AVOID"

st.subheader(
    "Final Verdict"
)

st.success(verdict)

tickers = st.multiselect(
    "Compare Stocks",
    ["NVDA","MSFT","TSLA","PLTR","MU","AAPL","GOOGL"],
    default=["NVDA","MSFT"]
)

data = yf.download(
    tickers,
    period="5y"
)

close = data["Close"]

returns = close.pct_change()

growth = 100 * (
    1 + returns
).cumprod()

fig = px.line(
    growth,
    title="Growth of $100"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

corr = returns.corr()
import plotly.figure_factory as ff

fig = ff.create_annotated_heatmap(
    z=corr.values,
    x=list(corr.columns),
    y=list(corr.index)
)

st.plotly_chart(fig)

capital = st.number_input(
    "Investment Amount",
    value=10000
)

selected = st.multiselect(
    "Portfolio Stocks",
    tickers
)

weights = []
for stock in selected:

    weight = st.slider(
        stock,
        0,
        100,
        20
    )

    weights.append(weight)

weights = np.array(weights)

weights = weights / weights.sum()

annual_returns = (
    returns.mean()*252
)
portfolio_return = np.sum(
    annual_returns[selected] * weights
)

st.metric(
    "Expected Return",
    f"{portfolio_return*100:.2f}%"
)

cov_matrix = (
    returns.cov()*252
)

portfolio_volatility = np.sqrt(
    np.dot(
        weights.T,
        np.dot(
            cov_matrix.loc[selected,selected],
            weights
        )
    )
)

st.metric(
    "Portfolio Risk",
    f"{portfolio_volatility*100:.2f}%"
)

risk_free_rate = 0.04

sharpe = (
    portfolio_return
    -
    risk_free_rate
) / portfolio_volatility

st.metric(
    "Sharpe Ratio",
    f"{sharpe:.2f}"
)

score = 50
if portfolio_return > 0.15:
    score += 20
if portfolio_volatility < 0.25:
    score += 15
if sharpe > 1:
    score += 15
st.metric(
    "Portfolio Score",
    f"{score}/100"
)

if sharpe < 1:

    suggestion = """
Increase diversification.

Reduce concentration risk.

Add lower volatility stocks.
"""

suggestion = """
Portfolio appears balanced.

Risk-adjusted returns are attractive.
"""

st.info(suggestion)

NVDA
MSFT
PLTR
TSLA

Current Price

Daily Change

Volume

Market Cap

stock.info

stock.fast_info

@st.cache_data
def load_data(ticker):

    return yf.download(
        ticker,
        period="5y"
    )

