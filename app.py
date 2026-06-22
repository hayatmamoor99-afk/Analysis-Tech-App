"""
StockLens Pro — Pure Mathematical Stock Analysis
requirements.txt:
    streamlit
    yfinance
    plotly
    pandas
    numpy
    anthropic
Run: streamlit run stocklens_app.py
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StockLens Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""<style>
.stApp{background:#070b14;color:#e2e8f0}
.main .block-container{padding:1.2rem 2rem;max-width:1400px}
[data-testid="stSidebar"]{background:#0d1117;border-right:1px solid #1e2d45}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] label{color:#94a3b8!important}
.stTextInput>div>div>input{background:#0d1117!important;border:1px solid #3b82f6!important;
    border-radius:8px!important;color:#fff!important;font-size:18px!important;
    font-weight:700!important;padding:12px 16px!important}
.stButton>button{background:linear-gradient(135deg,#3b82f6,#8b5cf6)!important;
    color:#fff!important;border:none!important;border-radius:8px!important;
    font-weight:700!important;width:100%}
.stButton>button:hover{opacity:.85!important}
[data-testid="stMetric"]{background:#0d1117;border:1px solid #1e2d45;border-radius:10px;padding:10px 14px}
[data-testid="stMetricLabel"]{color:#64748b!important;font-size:10px!important}
[data-testid="stMetricValue"]{color:#e2e8f0!important;font-size:16px!important}
.sec{font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:1px;
    margin:20px 0 12px;border-bottom:1px solid #1e2d45;padding-bottom:6px;display:flex;align-items:center;gap:8px}
.card{background:#0d1117;border:1px solid #1e2d45;border-radius:12px;padding:18px}
.stat-card{background:#0d1117;border:1px solid #1e2d45;border-radius:10px;
    padding:14px;text-align:center}
.stat-lbl{font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}
.stat-val{font-size:20px;font-weight:800}
.stat-sub{font-size:11px;color:#64748b;margin-top:3px}
.signal-pill{display:inline-block;padding:3px 10px;border-radius:20px;
    font-size:11px;font-weight:700;margin:2px}
.guide{background:#070b14;border:1px solid #1e2d45;border-radius:8px;
    padding:10px 12px;margin-bottom:8px}
.guide-title{font-size:12px;font-weight:700;color:#3b82f6;margin-bottom:3px}
.guide-body{font-size:11px;color:#64748b;line-height:1.6}
.verdict-box{border-radius:12px;padding:22px;border:1px solid}
.disc{background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.25);
    border-radius:8px;padding:10px 14px;font-size:11px;color:#b45309;margin-top:12px}
.stTabs [data-baseweb="tab-list"]{background:#0d1117;border-radius:8px;padding:4px;gap:4px}
.stTabs [data-baseweb="tab"]{background:transparent;color:#64748b;border-radius:6px;font-weight:600}
.stTabs [aria-selected="true"]{background:#3b82f6!important;color:#fff!important}
#MainMenu,footer,header{visibility:hidden}
</style>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA FUNCTIONS (all cached)
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300, show_spinner=False)
def load_stock(ticker):
    tk   = yf.Ticker(ticker)
    info = tk.info
    end  = datetime.today()

    # Monthly history for charts & long-term stats
    hist_mo = tk.history(start=end - timedelta(days=5*365), end=end, interval="1mo")
    if hist_mo.empty:
        raise ValueError(f"No data found for '{ticker}'. Check the symbol.")

    # Daily history for precise indicators (1 yr)
    hist_d = tk.history(start=end - timedelta(days=365), end=end, interval="1d")

    for h in [hist_mo, hist_d]:
        if h.index.tz is not None:
            h.index = h.index.tz_localize(None)

    hist_mo = hist_mo[["Close"]].dropna()
    hist_d  = hist_d[["Close","Volume"]].dropna() if not hist_d.empty else hist_mo.copy()

    periods = {
        "5yr": hist_mo,
        "4yr": hist_mo[hist_mo.index >= end - timedelta(days=4*365)],
        "3yr": hist_mo[hist_mo.index >= end - timedelta(days=3*365)],
        "2yr": hist_mo[hist_mo.index >= end - timedelta(days=2*365)],
        "1yr": hist_mo[hist_mo.index >= end - timedelta(days=365)],
    }

    cp = float(info.get("currentPrice") or info.get("regularMarketPrice") or hist_mo["Close"].iloc[-1])
    pc = float(info.get("previousClose") or info.get("regularMarketPreviousClose") or hist_mo["Close"].iloc[-2])

    return {
        "ticker":        ticker.upper(),
        "name":          info.get("longName") or info.get("shortName") or ticker.upper(),
        "price":         round(cp, 2),
        "prev_close":    round(pc, 2),
        "market_cap":    info.get("marketCap"),
        "pe":            info.get("trailingPE") or info.get("forwardPE"),
        "high52":        info.get("fiftyTwoWeekHigh"),
        "low52":         info.get("fiftyTwoWeekLow"),
        "avg_vol":       info.get("averageVolume"),
        "dividend":      info.get("dividendYield"),
        "sector":        info.get("sector", "N/A"),
        "country":       info.get("country", "N/A"),
        "beta":          info.get("beta"),
        "ma50":          info.get("fiftyDayAverage"),
        "ma200":         info.get("twoHundredDayAverage"),
        "periods":       periods,
        "daily":         hist_d,
    }


@st.cache_data(ttl=300, show_spinner=False)
def load_spy():
    end   = datetime.today()
    spy   = yf.Ticker("^GSPC").history(start=end - timedelta(days=5*365), end=end, interval="1mo")
    if spy.index.tz is not None:
        spy.index = spy.index.tz_localize(None)
    return spy[["Close"]].dropna()


# ═══════════════════════════════════════════════════════════════════════════════
# MATHEMATICAL INDICATORS
# ═══════════════════════════════════════════════════════════════════════════════

def calc_rsi(prices, period=14):
    delta  = prices.diff()
    gain   = delta.clip(lower=0)
    loss   = -delta.clip(upper=0)
    avg_g  = gain.ewm(com=period-1, min_periods=period).mean()
    avg_l  = loss.ewm(com=period-1, min_periods=period).mean()
    rs     = avg_g / avg_l.replace(0, np.nan)
    return round(float(100 - 100/(1+rs.iloc[-1])), 1)


def calc_macd(prices):
    ema12  = prices.ewm(span=12, adjust=False).mean()
    ema26  = prices.ewm(span=26, adjust=False).mean()
    macd   = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist   = macd - signal
    return round(float(macd.iloc[-1]),2), round(float(signal.iloc[-1]),2), round(float(hist.iloc[-1]),2)


def calc_bollinger(prices, period=20):
    sma  = prices.rolling(period).mean()
    std  = prices.rolling(period).std()
    up   = sma + 2*std
    dn   = sma - 2*std
    curr = float(prices.iloc[-1])
    bw   = float((up.iloc[-1] - dn.iloc[-1]) / sma.iloc[-1] * 100)
    pct  = float((curr - dn.iloc[-1]) / (up.iloc[-1] - dn.iloc[-1]) * 100)
    return round(float(up.iloc[-1]),2), round(float(sma.iloc[-1]),2), round(float(dn.iloc[-1]),2), round(bw,2), round(pct,1)


def calc_atr(daily, period=14):
    h = daily["Close"].rolling(2).max()
    l = daily["Close"].rolling(2).min()
    tr = h - l
    atr = tr.rolling(period).mean().iloc[-1]
    return round(float(atr), 2)


def calc_risk_metrics(hist_mo, spy_mo):
    r  = hist_mo["Close"].pct_change().dropna()
    rs = spy_mo["Close"].pct_change().dropna()

    # Align
    r, rs = r.align(rs, join="inner")

    ann = np.sqrt(12)
    mu  = float(r.mean())
    sd  = float(r.std())

    sharpe  = round(float((mu / sd) * ann), 2) if sd else 0
    neg     = r[r < 0]
    sortino = round(float((mu / neg.std()) * ann), 2) if len(neg) > 1 else 0

    # Max drawdown
    cum = (1 + r).cumprod()
    peak = cum.cummax()
    dd   = (cum - peak) / peak
    max_dd = round(float(dd.min() * 100), 2)

    # Beta & correlation
    cov  = np.cov(r.values, rs.values)
    beta = round(float(cov[0,1] / cov[1,1]), 2) if cov[1,1] else 1.0
    corr = round(float(np.corrcoef(r.values, rs.values)[0,1]), 2)

    # VaR & Expected Shortfall (95%)
    var95 = round(float(np.percentile(r, 5) * 100), 2)
    es95  = round(float(r[r <= np.percentile(r, 5)].mean() * 100), 2)

    # Annualised return & vol
    ann_ret = round(float(mu * 12 * 100), 2)
    ann_vol = round(float(sd * ann * 100), 2)

    # Calmar ratio
    calmar = round(float(ann_ret / abs(max_dd)), 2) if max_dd else 0

    return {
        "sharpe": sharpe, "sortino": sortino, "max_dd": max_dd,
        "beta": beta, "corr": corr,
        "var95": var95, "es95": es95,
        "ann_ret": ann_ret, "ann_vol": ann_vol,
        "calmar": calmar,
    }


def calc_momentum(hist_mo):
    c = hist_mo["Close"].dropna()
    def pct(n):
        if len(c) > n:
            return round(float((c.iloc[-1]-c.iloc[-n])/c.iloc[-n]*100), 2)
        return None
    return {"1mo": pct(1), "3mo": pct(3), "6mo": pct(6), "12mo": pct(12)}


def build_score(rsi, macd_val, macd_sig, bb_pct, rm, mom):
    """
    Composite mathematical score 0–100.
    Components: RSI, MACD crossover, Bollinger position,
                trend momentum, risk-adjusted return (Sharpe), VaR
    """
    score = 50

    # RSI (20 pts)
    if   rsi < 30: score += 15
    elif rsi < 45: score += 7
    elif rsi > 70: score -= 15
    elif rsi > 55: score -= 5

    # MACD crossover (15 pts)
    if macd_val > macd_sig: score += 10
    else:                   score -= 10

    # Bollinger Band position (10 pts)
    # <20% = near lower band (oversold), >80% = near upper (overbought)
    if   bb_pct < 20: score += 8
    elif bb_pct > 80: score -= 8

    # Momentum 6-month (15 pts)
    m6 = mom.get("6mo") or 0
    if   m6 > 15:  score += 12
    elif m6 > 5:   score += 6
    elif m6 < -15: score -= 12
    elif m6 < -5:  score -= 6

    # Sharpe ratio (10 pts)
    s = rm["sharpe"]
    if   s > 1.5: score += 8
    elif s > 0.5: score += 4
    elif s < 0:   score -= 8

    # VaR penalty (bad = large negative VaR, good = small)
    if rm["var95"] < -5: score -= 5

    score = max(0, min(100, score))

    if   score >= 60: return score, "BUY",  "#10b981", "🚀"
    elif score <= 38: return score, "SELL", "#ef4444", "⛔"
    else:             return score, "HOLD", "#f59e0b", "⏸️"


def run_monte_carlo(hist_mo, days=252, sims=500, investment=1000):
    c  = hist_mo["Close"].dropna().values.astype(float)
    r  = np.diff(c) / c[:-1]
    mu = float(np.mean(r))
    sg = float(np.std(r))
    S0 = c[-1]

    np.random.seed(42)
    paths       = np.zeros((sims, days))
    paths[:,0]  = S0
    for t in range(1, days):
        z = np.random.standard_normal(sims)
        paths[:,t] = paths[:,t-1] * np.exp((mu - .5*sg**2) + sg*z)

    finals = paths[:,-1]
    shares = investment / S0
    return {
        "paths":  paths, "finals": finals,
        "S0": S0, "shares": shares, "investment": investment,
        "days": days, "sims": sims,
        "mu": round(mu*100,3), "sigma": round(sg*100,3),
        "prob_up":   round(float(np.mean(finals>S0)*100),1),
        "prob_gt20": round(float(np.mean((finals-S0)/S0>0.2)*100),1),
        "prob_lt20": round(float(np.mean((finals-S0)/S0<-0.2)*100),1),
        "p5":  round(float(np.percentile(finals,5)),2),
        "p25": round(float(np.percentile(finals,25)),2),
        "p50": round(float(np.percentile(finals,50)),2),
        "p75": round(float(np.percentile(finals,75)),2),
        "p95": round(float(np.percentile(finals,95)),2),
        "mean": round(float(np.mean(finals)),2),
    }


def simulate_100(hist_mo, amount=100):
    c = hist_mo["Close"].dropna().values.astype(float)
    if len(c) < 2: return {"value": amount, "gain": 0, "pct": 0}
    v = round(amount/c[0]*c[-1], 2)
    return {"value": v, "gain": round(v-amount,2), "pct": round((c[-1]-c[0])/c[0]*100,2)}


# ═══════════════════════════════════════════════════════════════════════════════
# CHART BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════

DARK = dict(paper_bgcolor="#070b14", plot_bgcolor="#0d1117",
            font=dict(family="Inter,sans-serif",color="#94a3b8"),
            margin=dict(l=8,r=8,t=40,b=8),
            xaxis=dict(gridcolor="#1e2d45",showgrid=True,zeroline=False,
                       tickfont=dict(size=10),showline=False),
            yaxis=dict(gridcolor="#1e2d45",showgrid=True,zeroline=False,
                       tickfont=dict(size=10),showline=False),
            hovermode="x unified",
            hoverlabel=dict(bgcolor="#1a2235",font=dict(color="#e2e8f0")))


def chart_price(hist, ticker, label):
    c     = hist["Close"].dropna()
    is_up = float(c.iloc[-1]) >= float(c.iloc[0])
    color = "#10b981" if is_up else "#ef4444"
    fill  = "rgba(16,185,129,.07)" if is_up else "rgba(239,68,68,.07)"
    fig   = go.Figure()
    fig.add_trace(go.Scatter(x=c.index,y=c,fill="tozeroy",fillcolor=fill,
        line=dict(color=color,width=2.5),
        hovertemplate="<b>%{x|%b %Y}</b><br>$%{y:.2f}<extra></extra>",name=ticker))
    if len(c)>=6:
        fig.add_trace(go.Scatter(x=c.index,y=c.rolling(3).mean(),
            line=dict(color="rgba(139,92,246,.6)",width=1.5,dash="dot"),
            name="3-mo MA",hoverinfo="skip"))
    layout = {**DARK}
    layout["title"] = dict(text=f"{ticker} — {label}",font=dict(size=13,color="#e2e8f0"))
    layout["yaxis"]["tickprefix"] = "$"
    layout["height"] = 290
    fig.update_layout(**layout)
    return fig


def chart_macd(daily_prices, ticker):
    p      = daily_prices
    ema12  = p.ewm(span=12,adjust=False).mean()
    ema26  = p.ewm(span=26,adjust=False).mean()
    macd   = ema12 - ema26
    signal = macd.ewm(span=9,adjust=False).mean()
    hist_v = macd - signal

    fig = go.Figure()
    colors = ["#10b981" if v>=0 else "#ef4444" for v in hist_v]
    fig.add_trace(go.Bar(x=p.index,y=hist_v,marker_color=colors,name="Histogram",opacity=.7))
    fig.add_trace(go.Scatter(x=p.index,y=macd,line=dict(color="#3b82f6",width=1.8),name="MACD"))
    fig.add_trace(go.Scatter(x=p.index,y=signal,line=dict(color="#f59e0b",width=1.8),name="Signal"))
    layout = {**DARK}
    layout["title"] = dict(text=f"{ticker} — MACD (12,26,9)",font=dict(size=13,color="#e2e8f0"))
    layout["height"] = 240
    layout["legend"] = dict(bgcolor="rgba(0,0,0,0)",font=dict(size=11))
    fig.update_layout(**layout)
    return fig


def chart_bollinger(daily_prices, ticker):
    p   = daily_prices
    sma = p.rolling(20).mean()
    std = p.rolling(20).std()
    up  = sma + 2*std
    dn  = sma - 2*std

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=p.index,y=up,line=dict(color="rgba(59,130,246,.3)",width=1),
        name="Upper Band",hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=p.index,y=dn,line=dict(color="rgba(59,130,246,.3)",width=1),
        fill="tonexty",fillcolor="rgba(59,130,246,.05)",name="Lower Band",hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=p.index,y=sma,line=dict(color="#60a5fa",width=1.5,dash="dot"),
        name="SMA(20)",hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=p.index,y=p,line=dict(color="#e2e8f0",width=2),
        hovertemplate="<b>%{x|%b %d}</b><br>$%{y:.2f}<extra></extra>",name=ticker))
    layout = {**DARK}
    layout["title"] = dict(text=f"{ticker} — Bollinger Bands (20,2)",font=dict(size=13,color="#e2e8f0"))
    layout["yaxis"]["tickprefix"] = "$"
    layout["height"] = 260
    layout["legend"] = dict(bgcolor="rgba(0,0,0,0)",font=dict(size=11))
    fig.update_layout(**layout)
    return fig


def chart_rsi(daily_prices, ticker):
    r = daily_prices
    d = r.diff()
    g = d.clip(lower=0).ewm(com=13,min_periods=14).mean()
    l = (-d.clip(upper=0)).ewm(com=13,min_periods=14).mean()
    rsi_series = 100 - 100/(1 + g/l.replace(0,np.nan))

    fig = go.Figure()
    fig.add_hrect(y0=70,y1=100,fillcolor="rgba(239,68,68,.08)",line_width=0)
    fig.add_hrect(y0=0, y1=30, fillcolor="rgba(16,185,129,.08)",line_width=0)
    fig.add_hline(y=70,line=dict(color="#ef4444",width=1,dash="dot"))
    fig.add_hline(y=30,line=dict(color="#10b981",width=1,dash="dot"))
    fig.add_hline(y=50,line=dict(color="#64748b",width=1,dash="dot"))
    colors = ["#10b981" if v<=50 else "#f59e0b" if v<=70 else "#ef4444" for v in rsi_series]
    fig.add_trace(go.Scatter(x=rsi_series.index,y=rsi_series,
        line=dict(color="#a78bfa",width=2),
        hovertemplate="<b>%{x|%b %d}</b><br>RSI: %{y:.1f}<extra></extra>",name="RSI(14)"))
    layout = {**DARK}
    layout["title"] = dict(text=f"{ticker} — RSI (14)",font=dict(size=13,color="#e2e8f0"))
    layout["yaxis"]["range"] = [0,100]
    layout["yaxis"]["ticksuffix"] = ""
    layout["height"] = 220
    fig.update_layout(**layout)
    return fig


def chart_mc_paths(mc, ticker):
    paths = mc["paths"]
    days  = mc["days"]
    x     = list(range(days))
    fig   = go.Figure()

    step = max(1, len(paths)//60)
    for i in range(0, len(paths), step):
        col = "rgba(16,185,129,.07)" if paths[i,-1]>mc["S0"] else "rgba(239,68,68,.07)"
        fig.add_trace(go.Scatter(x=x,y=paths[i],mode="lines",
            line=dict(color=col,width=1),showlegend=False,hoverinfo="skip"))

    p5  = np.percentile(paths,5, axis=0)
    p25 = np.percentile(paths,25,axis=0)
    p75 = np.percentile(paths,75,axis=0)
    p95 = np.percentile(paths,95,axis=0)
    med = np.percentile(paths,50,axis=0)

    fig.add_trace(go.Scatter(x=x+x[::-1],y=list(p95)+list(p5[::-1]),
        fill="toself",fillcolor="rgba(59,130,246,.06)",
        line=dict(color="rgba(0,0,0,0)"),name="5–95th pct"))
    fig.add_trace(go.Scatter(x=x+x[::-1],y=list(p75)+list(p25[::-1]),
        fill="toself",fillcolor="rgba(59,130,246,.12)",
        line=dict(color="rgba(0,0,0,0)"),name="25–75th pct"))
    fig.add_trace(go.Scatter(x=x,y=med,line=dict(color="#60a5fa",width=2.5),name="Median"))
    fig.add_trace(go.Scatter(x=x,y=[mc["S0"]]*days,
        line=dict(color="#64748b",width=1.5,dash="dash"),name="Current price"))

    layout = {**DARK}
    layout["title"] = dict(
        text=f"{ticker} — Monte Carlo ({mc['sims']} paths, {mc['days']} trading days)",
        font=dict(size=13,color="#e2e8f0"))
    layout["yaxis"]["tickprefix"] = "$"
    layout["height"] = 340
    layout["legend"] = dict(bgcolor="rgba(0,0,0,0)",font=dict(size=11),
        orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1)
    fig.update_layout(**layout)
    return fig


def chart_mc_dist(mc, ticker):
    finals = mc["finals"]
    S0     = mc["S0"]
    fig    = go.Figure()
    fig.add_trace(go.Histogram(
        x=finals, nbinsx=50, opacity=.85,
        marker=dict(color=["#10b981" if p>S0 else "#ef4444" for p in finals],line=dict(width=0)),
        name="Final price"))
    for val, lbl, col in [
        (mc["p5"],"5th","#ef4444"),(mc["p25"],"25th","#f59e0b"),
        (mc["p50"],"Median","#60a5fa"),(mc["p75"],"75th","#a78bfa"),
        (mc["p95"],"95th","#10b981"),(S0,"Current","#ffffff"),
    ]:
        fig.add_vline(x=val,line=dict(color=col,width=1.5,dash="dot"),
            annotation_text=lbl,annotation_font=dict(size=9,color=col))
    layout = {**DARK}
    layout["title"] = dict(text=f"{ticker} — Final Price Distribution",font=dict(size=13,color="#e2e8f0"))
    layout["xaxis"]["tickprefix"] = "$"
    layout["height"] = 300
    layout["showlegend"] = False
    layout["bargap"] = 0.02
    fig.update_layout(**layout)
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# AI ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def get_ai_analysis(d, rm, indicators, score, verdict, mc):
    key = st.session_state.get("api_key","").strip()
    if not key:
        return "💡 Enter your Anthropic API key in the sidebar to enable AI analysis."
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        inv5   = simulate_100(d["periods"]["5yr"])
        inv1   = simulate_100(d["periods"]["1yr"])
        prompt = (
            f"You are a quantitative analyst. Write a professional 5-sentence analysis for "
            f"{d['ticker']} ({d['name']}, sector: {d['sector']}) based ONLY on mathematical data.\n\n"
            f"PRICE: ${d['price']} | 5yr return: {inv5['pct']}% | 1yr return: {inv1['pct']}%\n"
            f"INDICATORS: RSI={indicators['rsi']} | MACD={indicators['macd']} vs Signal={indicators['macd_sig']} "
            f"| BB%={indicators['bb_pct']}% | ATR=${indicators['atr']}\n"
            f"RISK METRICS: Sharpe={rm['sharpe']} | Sortino={rm['sortino']} | Max Drawdown={rm['max_dd']}% "
            f"| Beta={rm['beta']} | VaR(95%)={rm['var95']}% | Ann.Return={rm['ann_ret']}% | Ann.Vol={rm['ann_vol']}%\n"
            f"MOMENTUM: 1mo={indicators['mom1']}% | 3mo={indicators['mom3']}% | 6mo={indicators['mom6']}% | 12mo={indicators['mom12']}%\n"
            f"MONTE CARLO ({mc['days']}d): P(profit)={mc['prob_up']}% | Median=${mc['p50']} | "
            f"Bear(p5)=${mc['p5']} | Bull(p95)=${mc['p95']}\n"
            f"SIGNAL: {verdict} | Score={score}/100\n\n"
            f"Write 5 sentences: (1) historical return & risk-adjusted performance using Sharpe/Sortino, "
            f"(2) technical indicator reading (RSI, MACD, Bollinger), "
            f"(3) risk profile using VaR, drawdown, beta & volatility, "
            f"(4) Monte Carlo probability outlook, "
            f"(5) overall verdict with key risk factor. Be precise and cite numbers."
        )
        msg = client.messages.create(model="claude-sonnet-4-6", max_tokens=500,
                                     messages=[{"role":"user","content":prompt}])
        return msg.content[0].text
    except Exception as e:
        return f"AI analysis unavailable: {e}"


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

def fmt(n):
    if n is None: return "N/A"
    n = float(n)
    if n>=1e12: return f"${n/1e12:.2f}T"
    if n>=1e9:  return f"${n/1e9:.2f}B"
    if n>=1e6:  return f"${n/1e6:.2f}M"
    return f"{n:,.0f}"


with st.sidebar:
    st.markdown("""<div style="text-align:center;padding:8px 0 14px">
        <div style="font-size:26px">📊</div>
        <div style="font-size:18px;font-weight:800;background:linear-gradient(135deg,#60a5fa,#a78bfa);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent">StockLens Pro</div>
        <div style="font-size:10px;color:#64748b">Mathematical Stock Analysis</div>
    </div>""", unsafe_allow_html=True)

    api_key = st.text_input("🔑 Anthropic API Key (optional)",
                             type="password", placeholder="sk-ant-...")
    if api_key:
        st.session_state["api_key"] = api_key

    st.markdown("---")
    st.markdown("**📚 What Each Indicator Means**")
    for title, body in [
        ("📈 RSI","Momentum 0–100. Below 30 = oversold (possible buy). Above 70 = overbought (possible sell)."),
        ("📉 MACD","When MACD line crosses above Signal line → bullish. Below → bearish."),
        ("🎯 Bollinger Bands","Price vs 20-day average ± 2 standard deviations. Near lower band = oversold. Near upper = overbought."),
        ("⚡ Sharpe Ratio","Return per unit of risk. >1 = good. >2 = excellent. Negative = return worse than risk-free rate."),
        ("🛡️ Sortino Ratio","Like Sharpe but only penalises downside volatility. Higher = better."),
        ("📉 Max Drawdown","Biggest peak-to-trough loss ever. -30% means stock once fell 30% from its peak."),
        ("🎲 VaR 95%","Value at Risk. In the worst 5% of months, you'd lose at least this much %."),
        ("🔗 Beta","Market sensitivity. Beta>1 = amplifies market moves. Beta<1 = more stable than market."),
        ("🎲 Monte Carlo","Runs 500 simulated futures using your stock's own historical drift & volatility (GBM model)."),
    ]:
        st.markdown(f'<div class="guide"><div class="guide-title">{title}</div>'
                    f'<div class="guide-body">{body}</div></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN UI
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""<div style="text-align:center;padding:6px 0 10px">
    <span style="font-size:24px;font-weight:900;background:linear-gradient(135deg,#60a5fa,#a78bfa,#34d399);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent">📊 StockLens Pro</span>
    <div style="font-size:11px;color:#64748b;margin-top:2px">
        RSI · MACD · Bollinger · Sharpe · VaR · Monte Carlo — 100% Mathematical
    </div>
</div>""", unsafe_allow_html=True)

# Search
c1, c2 = st.columns([4,1])
with c1:
    ticker_input = st.text_input("Ticker","",
        placeholder="Enter ticker: AAPL, TSLA, NVDA, RELIANCE.NS ...",
        label_visibility="collapsed", key="tf").upper().strip()
with c2:
    go_btn = st.button("🔍 Analyse", use_container_width=True)

# Quick picks
qc = st.columns(8)
for col, qt in zip(qc, ["AAPL","MSFT","GOOGL","TSLA","AMZN","NVDA","META","JPM"]):
    with col:
        if st.button(qt, key=f"q_{qt}"):
            st.session_state["run"] = qt
            st.rerun()

st.markdown("<hr style='border-color:#1e2d45;margin:10px 0'>", unsafe_allow_html=True)

final = st.session_state.pop("run", None) or (ticker_input if go_btn else None)

if not final:
    st.markdown("""<div style="text-align:center;padding:60px 20px;color:#64748b">
        <div style="font-size:48px;margin-bottom:12px">📊</div>
        <div style="font-size:16px;font-weight:600;color:#94a3b8;margin-bottom:6px">
            Search any stock above to begin
        </div>
        <div style="font-size:13px;margin-bottom:20px">
            Powered entirely by mathematics — no news, no noise
        </div>
        <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap">
            <span style="background:rgba(59,130,246,.12);color:#60a5fa;font-size:11px;font-weight:600;padding:5px 14px;border-radius:20px">📈 RSI · MACD · Bollinger</span>
            <span style="background:rgba(139,92,246,.12);color:#a78bfa;font-size:11px;font-weight:600;padding:5px 14px;border-radius:20px">⚡ Sharpe · Sortino · VaR</span>
            <span style="background:rgba(16,185,129,.12);color:#34d399;font-size:11px;font-weight:600;padding:5px 14px;border-radius:20px">🎲 Monte Carlo Simulation</span>
            <span style="background:rgba(245,158,11,.12);color:#fbbf24;font-size:11px;font-weight:600;padding:5px 14px;border-radius:20px">💰 $100 Investment Sim</span>
        </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Load ──────────────────────────────────────────────────────────────────────
prog = st.progress(0, text="📡 Fetching stock data...")
try:
    d = load_stock(final)
except Exception as e:
    st.error(f"⚠️ {e}")
    st.stop()

prog.progress(50, text="📊 Loading S&P 500 benchmark...")
spy = load_spy()

prog.progress(80, text="🔢 Computing indicators...")
tech5  = compute_technicals_full = d["periods"]["5yr"]
daily  = d["daily"]
prices = daily["Close"] if "Close" in daily.columns else d["periods"]["1yr"]["Close"]

rsi_val                          = calc_rsi(prices)
macd_val, macd_sig, macd_hist    = calc_macd(prices)
bb_up, bb_mid, bb_dn, bb_bw, bb_pct = calc_bollinger(prices)
atr_val                          = calc_atr(daily) if "Close" in daily.columns else 0
rm                               = calc_risk_metrics(d["periods"]["5yr"], spy)
mom                              = calc_momentum(d["periods"]["5yr"])
score, verdict, v_color, v_icon  = build_score(rsi_val, macd_val, macd_sig, bb_pct, rm, mom)

indicators = {
    "rsi": rsi_val, "macd": macd_val, "macd_sig": macd_sig,
    "macd_hist": macd_hist, "bb_pct": bb_pct, "atr": atr_val,
    "mom1": mom["1mo"], "mom3": mom["3mo"],
    "mom6": mom["6mo"], "mom12": mom["12mo"],
}

prog.progress(100, text="✅ Done!")
prog.empty()

# ── Price Header ──────────────────────────────────────────────────────────────
change     = d["price"] - d["prev_close"]
change_pct = change / d["prev_close"] * 100 if d["prev_close"] else 0
is_up      = change >= 0
dc         = "#10b981" if is_up else "#ef4444"

a1, a2 = st.columns([2,1])
with a1:
    st.markdown(f"""<div>
        <span style="font-size:30px;font-weight:900;color:#fff">{d['ticker']}</span>
        <span style="margin-left:10px;font-size:13px;color:#64748b">{d['name']}</span>
    </div>
    <div style="font-size:11px;color:#64748b;margin-top:2px">
        {d['sector']} · {d['country']} · Beta: {d.get('beta','N/A')}
    </div>""", unsafe_allow_html=True)
with a2:
    st.markdown(f"""<div style="text-align:right">
        <div style="font-size:30px;font-weight:900;color:#fff">${d['price']:,.2f}</div>
        <div style="font-size:13px;font-weight:700;color:{dc}">
            {'▲' if is_up else '▼'} ${abs(change):.2f} ({'+' if is_up else ''}{change_pct:.2f}%)
        </div>
    </div>""", unsafe_allow_html=True)

# ── Key Metrics Row ───────────────────────────────────────────────────────────
st.markdown('<div class="sec">📊 Key Metrics</div>', unsafe_allow_html=True)
for col, (lbl, val) in zip(st.columns(8),[
    ("Market Cap",  fmt(d["market_cap"])),
    ("P/E Ratio",   f"{d['pe']:.1f}" if d["pe"] else "N/A"),
    ("52W High",    f"${d['high52']:.2f}" if d["high52"] else "N/A"),
    ("52W Low",     f"${d['low52']:.2f}"  if d["low52"]  else "N/A"),
    ("MA 50",       f"${d['ma50']:.2f}"   if d["ma50"]   else "N/A"),
    ("MA 200",      f"${d['ma200']:.2f}"  if d["ma200"]  else "N/A"),
    ("Ann. Return", f"{rm['ann_ret']}%"),
    ("Ann. Vol",    f"{rm['ann_vol']}%"),
]):
    col.metric(lbl, val)

# ── Technical Indicators ──────────────────────────────────────────────────────
st.markdown('<div class="sec">📈 Technical Indicators</div>', unsafe_allow_html=True)

ti_cols = st.columns(4)

rsi_color = "#10b981" if rsi_val<30 else "#ef4444" if rsi_val>70 else "#f59e0b"
rsi_lbl   = "Oversold 🟢" if rsi_val<30 else "Overbought 🔴" if rsi_val>70 else "Neutral 🟡"
ti_cols[0].markdown(f"""<div class="stat-card">
    <div class="stat-lbl">RSI (14-day)</div>
    <div class="stat-val" style="color:{rsi_color}">{rsi_val}</div>
    <div class="stat-sub">{rsi_lbl}</div>
</div>""", unsafe_allow_html=True)

macd_color = "#10b981" if macd_val>macd_sig else "#ef4444"
macd_lbl   = "Bullish cross 🟢" if macd_val>macd_sig else "Bearish cross 🔴"
ti_cols[1].markdown(f"""<div class="stat-card">
    <div class="stat-lbl">MACD</div>
    <div class="stat-val" style="color:{macd_color}">{macd_val}</div>
    <div class="stat-sub">Signal: {macd_sig} · {macd_lbl}</div>
</div>""", unsafe_allow_html=True)

bb_color = "#10b981" if bb_pct<20 else "#ef4444" if bb_pct>80 else "#e2e8f0"
bb_lbl   = "Near lower (oversold)" if bb_pct<20 else "Near upper (overbought)" if bb_pct>80 else "Mid-range"
ti_cols[2].markdown(f"""<div class="stat-card">
    <div class="stat-lbl">Bollinger Band %</div>
    <div class="stat-val" style="color:{bb_color}">{bb_pct}%</div>
    <div class="stat-sub">{bb_lbl}</div>
</div>""", unsafe_allow_html=True)

ti_cols[3].markdown(f"""<div class="stat-card">
    <div class="stat-lbl">ATR (14-day)</div>
    <div class="stat-val" style="color:#a78bfa">${atr_val}</div>
    <div class="stat-sub">Average true range</div>
</div>""", unsafe_allow_html=True)

# Indicator Charts
ic_tab1, ic_tab2, ic_tab3 = st.tabs(["📉 RSI", "📊 MACD", "🎯 Bollinger Bands"])
with ic_tab1:
    st.plotly_chart(chart_rsi(prices, d["ticker"]), use_container_width=True)
with ic_tab2:
    st.plotly_chart(chart_macd(prices, d["ticker"]), use_container_width=True)
with ic_tab3:
    st.plotly_chart(chart_bollinger(prices, d["ticker"]), use_container_width=True)

# ── Risk Metrics ──────────────────────────────────────────────────────────────
st.markdown('<div class="sec">🛡️ Risk & Performance Metrics</div>', unsafe_allow_html=True)

rm_cols = st.columns(5)
for col, (lbl, val, sub, good_hi) in zip(rm_cols, [
    ("Sharpe Ratio",  rm["sharpe"],  ">1 good, >2 excellent", True),
    ("Sortino Ratio", rm["sortino"], "Downside-adjusted",     True),
    ("Max Drawdown",  f"{rm['max_dd']}%", "Worst peak→trough loss", False),
    ("VaR (95%)",     f"{rm['var95']}%",  "Monthly worst 5% loss",  False),
    ("Calmar Ratio",  rm["calmar"],  "Return / Max Drawdown", True),
]):
    is_good = (float(str(val).replace('%','')) > 0) if good_hi else (float(str(val).replace('%','')) > -10)
    c = "#10b981" if is_good else "#ef4444"
    col.markdown(f"""<div class="stat-card">
        <div class="stat-lbl">{lbl}</div>
        <div class="stat-val" style="color:{c}">{val}</div>
        <div class="stat-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

rm_cols2 = st.columns(5)
for col, (lbl, val, sub) in zip(rm_cols2, [
    ("Beta vs S&P",    rm["beta"],         "Market sensitivity"),
    ("Correlation",    rm["corr"],          "Corr. with S&P 500"),
    ("Exp. Shortfall", f"{rm['es95']}%",    "Avg loss beyond VaR"),
    ("Ann. Return",    f"{rm['ann_ret']}%", "Annualised return"),
    ("Ann. Volatility",f"{rm['ann_vol']}%", "Annualised std dev"),
]):
    c = "#10b981" if str(val).replace('%','').replace('-','').replace('.','').isdigit() and float(str(val).replace('%','')) >= 0 else "#ef4444"
    col.markdown(f"""<div class="stat-card">
        <div class="stat-lbl">{lbl}</div>
        <div class="stat-val" style="color:{c}">{val}</div>
        <div class="stat-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

# ── Price Charts ──────────────────────────────────────────────────────────────
st.markdown('<div class="sec">📈 Historical Price Charts</div>', unsafe_allow_html=True)
period_map = [("5yr","5 Year"),("4yr","4 Year"),("3yr","3 Year"),("2yr","2 Year"),("1yr","1 Year")]
for tab, (key, label) in zip(st.tabs([f"📅 {l}" for _,l in period_map]), period_map):
    with tab:
        h = d["periods"][key]
        st.plotly_chart(chart_price(h, d["ticker"], label), use_container_width=True) if not h.empty else st.warning(f"Not enough data.")

# ── $100 Investment Simulator ─────────────────────────────────────────────────
st.markdown('<div class="sec">💰 $100 Investment Simulator</div>', unsafe_allow_html=True)
for col, (key, label) in zip(st.columns(5), period_map):
    inv = simulate_100(d["periods"][key])
    pos = inv["gain"] >= 0
    c   = "#10b981" if pos else "#ef4444"
    col.markdown(f"""<div class="stat-card">
        <div class="stat-lbl">{label}</div>
        <div style="font-size:10px;color:#64748b;margin-bottom:4px">Started $100</div>
        <div class="stat-val" style="color:{c}">${inv['value']:,.2f}</div>
        <div class="stat-sub" style="color:{c}">{'+' if pos else ''}${inv['gain']:.2f} · {'▲' if pos else '▼'}{abs(inv['pct']):.1f}%</div>
    </div>""", unsafe_allow_html=True)

# ── Momentum ──────────────────────────────────────────────────────────────────
st.markdown('<div class="sec">⚡ Price Momentum</div>', unsafe_allow_html=True)
for col, (lbl, val) in zip(st.columns(4), [
    ("1 Month",  mom["1mo"]),
    ("3 Months", mom["3mo"]),
    ("6 Months", mom["6mo"]),
    ("12 Months",mom["12mo"]),
]):
    if val is None:
        col.markdown(f'<div class="stat-card"><div class="stat-lbl">{lbl}</div><div class="stat-val">N/A</div></div>', unsafe_allow_html=True)
    else:
        pos = val >= 0
        c   = "#10b981" if pos else "#ef4444"
        col.markdown(f"""<div class="stat-card">
            <div class="stat-lbl">{lbl}</div>
            <div class="stat-val" style="color:{c}">{'+' if pos else ''}{val}%</div>
            <div class="stat-sub">Price change</div>
        </div>""", unsafe_allow_html=True)

# ── Monte Carlo ───────────────────────────────────────────────────────────────
st.markdown('<div class="sec">🎲 Monte Carlo Price Simulation</div>', unsafe_allow_html=True)

mc1, mc2, mc3 = st.columns(3)
with mc1:
    mc_days = st.selectbox("Forecast Horizon",
        [63,126,252,504], index=2,
        format_func=lambda x:{63:"3 Months",126:"6 Months",252:"1 Year",504:"2 Years"}[x])
with mc2:
    mc_sims = st.selectbox("Simulations",[200,500,1000],index=1)
with mc3:
    mc_inv  = st.number_input("Investment ($)",min_value=100,max_value=1000000,value=1000,step=500)

mc = run_monte_carlo(d["periods"]["5yr"], days=mc_days, sims=mc_sims, investment=mc_inv)
exp_val  = round(mc["shares"] * mc["mean"], 2)
exp_gain = round(exp_val - mc_inv, 2)

# MC stat row
mc_stat_cols = st.columns(6)
for col, (lbl, val, sub, col_c) in zip(mc_stat_cols, [
    ("Prob. Profit",    f"{mc['prob_up']}%",    f"{round(100-mc['prob_up'],1)}% loss chance", "#10b981"),
    ("Prob. >+20%",     f"{mc['prob_gt20']}%",  "Chance of 20%+ gain",  "#3b82f6"),
    ("Prob. <-20%",     f"{mc['prob_lt20']}%",  "Chance of 20%+ loss",  "#ef4444"),
    ("Median Price",    f"${mc['p50']:,.2f}",    f"from ${mc['S0']:,.2f}","#60a5fa"),
    ("Expected Value",  f"${exp_val:,.2f}",      f"on ${mc_inv:,}",      "#10b981" if exp_gain>=0 else "#ef4444"),
    ("Price Range",     f"${mc['p5']:,.0f}–${mc['p95']:,.0f}","5th–95th pct","#a78bfa"),
]):
    col.markdown(f"""<div class="stat-card">
        <div class="stat-lbl">{lbl}</div>
        <div class="stat-val" style="color:{col_c}">{val}</div>
        <div class="stat-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

st.markdown(f"""<div style="font-size:11px;color:#64748b;margin:8px 0;padding:8px 12px;
    background:#0d1117;border:1px solid #1e2d45;border-radius:8px">
    📐 <b style="color:#94a3b8">Geometric Brownian Motion</b> &nbsp;|&nbsp;
    μ (monthly drift) = <span style="color:#60a5fa">{mc['mu']}%</span> &nbsp;|&nbsp;
    σ (monthly volatility) = <span style="color:#a78bfa">{mc['sigma']}%</span> &nbsp;|&nbsp;
    {mc['sims']} simulated paths · {mc['days']} trading days
</div>""", unsafe_allow_html=True)

mct1, mct2 = st.tabs(["📈 Simulation Paths","📊 Price Distribution"])
with mct1:
    st.plotly_chart(chart_mc_paths(mc, d["ticker"]), use_container_width=True)
with mct2:
    st.plotly_chart(chart_mc_dist(mc, d["ticker"]), use_container_width=True)

# Percentile outcome table
pct_cols = st.columns(5)
for col, (lbl, price, meaning) in zip(pct_cols, [
    ("Worst 5%",  mc["p5"],  "Bear case"),
    ("25th pct",  mc["p25"], "Below median"),
    ("Median",    mc["p50"], "Base case"),
    ("75th pct",  mc["p75"], "Above median"),
    ("Best 5%",   mc["p95"], "Bull case"),
]):
    pnl = round((price-mc["S0"])/mc["S0"]*100,1)
    pos = pnl >= 0
    cval= round(mc["shares"]*price,2)
    col.markdown(f"""<div class="stat-card">
        <div class="stat-lbl">{lbl} · {meaning}</div>
        <div class="stat-val" style="color:{'#10b981' if pos else '#ef4444'}">${price:,.2f}</div>
        <div class="stat-sub" style="color:{'#10b981' if pos else '#ef4444'}">{'+' if pos else ''}{pnl}%</div>
        <div style="font-size:10px;color:#64748b;margin-top:3px">${cval:,.0f} on ${mc_inv:,}</div>
    </div>""", unsafe_allow_html=True)

# ── Verdict ───────────────────────────────────────────────────────────────────
st.markdown('<div class="sec">🤖 Mathematical Verdict</div>', unsafe_allow_html=True)

vl, vr = st.columns([3,2])
with vl:
    vc  = {"BUY":"rgba(16,185,129,.08)","SELL":"rgba(239,68,68,.08)","HOLD":"rgba(245,158,11,.08)"}[verdict]
    bc  = {"BUY":"rgba(16,185,129,.3)","SELL":"rgba(239,68,68,.3)","HOLD":"rgba(245,158,11,.3)"}[verdict]
    bar = "█"*int(score/5) + "░"*(20-int(score/5))
    st.markdown(f"""<div style="background:{vc};border:1px solid {bc};border-radius:12px;padding:22px">
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:14px">
            <div style="font-size:40px">{v_icon}</div>
            <div>
                <div style="font-size:10px;font-weight:700;color:{v_color};text-transform:uppercase;letter-spacing:1px">Mathematical Signal</div>
                <div style="font-size:30px;font-weight:900;color:{v_color}">{verdict}</div>
            </div>
            <div style="margin-left:auto;text-align:right">
                <div style="font-size:10px;color:#64748b">Composite Score</div>
                <div style="font-size:30px;font-weight:900;color:{v_color}">{score}/100</div>
            </div>
        </div>
        <div style="font-size:10px;color:#64748b;font-family:monospace;letter-spacing:1px;margin-bottom:6px">{bar}</div>
        <div style="font-size:11px;color:#64748b">
            Scored on RSI ({indicators['rsi']}) · MACD crossover · Bollinger ({bb_pct}%) · 
            6-mo momentum ({mom['6mo']}%) · Sharpe ({rm['sharpe']}) · VaR ({rm['var95']}%)
        </div>
    </div>""", unsafe_allow_html=True)

with vr:
    for lbl, val, c in [
        ("RSI Signal",    rsi_lbl,                                  rsi_color),
        ("MACD Signal",   macd_lbl,                                  macd_color),
        ("Sharpe Ratio",  str(rm["sharpe"]),                         "#10b981" if rm["sharpe"]>1 else "#f59e0b" if rm["sharpe"]>0 else "#ef4444"),
        ("Max Drawdown",  f"{rm['max_dd']}%",                        "#ef4444" if rm["max_dd"]<-30 else "#f59e0b"),
        ("VaR (95%)",     f"{rm['var95']}% monthly",                 "#ef4444" if rm["var95"]<-5 else "#f59e0b"),
        ("MC Prob Profit",f"{mc['prob_up']}%",                       "#10b981" if mc["prob_up"]>60 else "#f59e0b"),
    ]:
        st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
            background:#070b14;border:1px solid #1e2d45;border-radius:8px;
            padding:9px 14px;margin-bottom:7px">
            <span style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:.5px">{lbl}</span>
            <span style="font-size:13px;font-weight:700;color:{c}">{val}</span>
        </div>""", unsafe_allow_html=True)

# ── AI Analysis ───────────────────────────────────────────────────────────────
st.markdown('<div class="sec">📝 AI Quantitative Analysis</div>', unsafe_allow_html=True)
with st.spinner("Generating quantitative analysis..."):
    analysis = get_ai_analysis(d, rm, indicators, score, verdict, mc)

st.markdown(f"""<div class="card">
    <div style="color:#94a3b8;font-size:14px;line-height:1.9">{analysis}</div>
</div>
<div class="disc">
</div>""", unsafe_allow_html=True)
