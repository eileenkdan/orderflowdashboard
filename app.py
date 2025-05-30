
import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from ta.trend import SMAIndicator, MACD
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator
from utils.finviz_data import get_finviz_stats
from utils.polygon_data import get_polygon_price

TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "RIVN", "FSLR", "HIMS", "BABA"]

st.set_page_config(layout="wide")
st.title("📊 Enhanced AI Stock Screener")

st.sidebar.header("🔍 Screener Filters")
min_pe = st.sidebar.slider("Max P/E", 1, 100, 40)
min_rsi = st.sidebar.slider("Min RSI", 0, 100, 30)
max_pb = st.sidebar.slider("Max Price/Book", 0.5, 20.0, 5.0)
polygon_api_key = st.secrets["POLYGON_API_KEY"]

@st.cache_data
def fetch_data(ticker):
    df = yf.download(ticker, period="6mo", interval="1d")
    if df.empty or 'Close' not in df:
        return None
    df.dropna(inplace=True)

    # Explicit 1D Series extraction
    close = pd.Series(df['Close'].values.flatten(), index=df.index)

    df['SMA50'] = SMAIndicator(close=close, window=50).sma_indicator()
    df['RSI'] = RSIIndicator(close=close).rsi()
    macd = MACD(close=close)
    df['MACD'] = macd.macd()
    bb = BollingerBands(close=close)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()

    return df

summary = []

for ticker in TICKERS:
    try:
        df = fetch_data(ticker)
        if df is None:
            continue
        info = yf.Ticker(ticker).info
        finviz = get_finviz_stats(ticker)

        pe = info.get('trailingPE', 0)
        pb = info.get('priceToBook', 0)
        roe = info.get('returnOnEquity', 0)
        fcf = info.get('freeCashflow', 0)
        rsi = df['RSI'].iloc[-1]
        macd_val = df['MACD'].iloc[-1]

        if pe > min_pe or pb > max_pb or rsi < min_rsi:
            continue

        score = 0
        score += 20 if rsi > 50 else 0
        score += 20 if macd_val > 0 else 0
        score += 20 if pe < 25 else 0
        score += 20 if pb < 3 else 0
        score += 20 if roe and roe > 0.1 else 0

        summary.append({
            "Ticker": ticker,
            "P/E": round(pe, 2),
            "P/B": round(pb, 2),
            "ROE": round(roe, 2) if roe else None,
            "RSI": round(rsi, 2),
            "MACD": round(macd_val, 2),
            "Short Float": finviz.get("Short Float", "N/A"),
            "Insider Own": finviz.get("Insider Own", "N/A"),
            "Live Price": get_polygon_price(ticker, polygon_api_key),
            "Score": score
        })

    except Exception as e:
        st.warning(f"{ticker} failed: {e}")

if summary:
    df_summary = pd.DataFrame(summary).sort_values(by="Score", ascending=False)
    st.dataframe(df_summary)

    st.subheader("📈 Chart View")
    selected_ticker = st.selectbox("Select Ticker", df_summary["Ticker"])
    chart_data = fetch_data(selected_ticker)
    fig, ax = plt.subplots()
    ax.plot(chart_data['Close'], label='Close')
    ax.plot(chart_data['SMA50'], label='SMA50', linestyle='--')
    ax.plot(chart_data['bb_upper'], label='BB Upper', linestyle=':')
    ax.plot(chart_data['bb_lower'], label='BB Lower', linestyle=':')
    ax.legend()
    st.pyplot(fig)
else:
    st.info("No stocks passed the filter criteria.")
