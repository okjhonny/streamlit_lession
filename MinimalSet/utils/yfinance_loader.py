# utils/yfinance_loader.py
# -----------------------------------------------------------------------------
# THE FUNCTION THAT CALLS YFINANCE
#
# yfinance is a library that downloads stock-market data from Yahoo Finance.
# This file contains ONE function, fetch_daily_data(), used by the
# "Stock Price" page. Keeping it here means any future page can import and
# reuse it with a single line:
#
#     from utils.yfinance_loader import fetch_daily_data
#
# NOTE: this function needs an internet connection to work.
# -----------------------------------------------------------------------------

import yfinance as yf
import pandas as pd
import streamlit as st


@st.cache_data  # remember the result so we do not download the same data twice
def fetch_daily_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Download daily stock data from Yahoo Finance.

    Args:
        symbol:     ticker symbol, e.g. "AAPL"
        start_date: first day, format "YYYY-MM-DD"
        end_date:   last day,  format "YYYY-MM-DD"

    Returns:
        A pandas DataFrame with one row per day (Open, High, Low, Close, Volume).
    """
    data = yf.download(symbol, start=start_date, end=end_date)

    # If Yahoo Finance returns nothing, give a clear error instead of a crash.
    if data is None or data.empty:
        raise ValueError(
            f"No data found for '{symbol}' between {start_date} and {end_date}."
        )
    return data


def close_series(data: pd.DataFrame) -> pd.Series:
    """Return the closing prices as a simple one-column Series."""
    close = data["Close"]
    # For a single ticker yfinance may return a DataFrame; take its column.
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return close


def rebase_to_100(series: pd.Series) -> pd.Series:
    """
    Rescale a price series so it starts at 100.
    This is the "normalisation" step: a $30 stock and the S&P 500 (~5000
    points) cannot be compared directly, but once both start at 100 you can
    compare their percentage growth on the same chart.
    """
    return series / series.dropna().iloc[0] * 100
