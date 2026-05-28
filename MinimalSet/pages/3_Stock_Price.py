# pages/3_Stock_Price.py
# =============================================================================
# PAGE 3 - STOCK PRICE  (yfinance + buttons + session_state)
# =============================================================================
# This page downloads a real stock price from Yahoo Finance and lets you
# compare it with the S&P 500 index, switched on/off by two buttons.
#
# It re-uses two ideas you have already seen:
#   - the yfinance function from utils/yfinance_loader.py
#   - st.session_state (Page 2) to remember whether "compare mode" is ON
#
# NOTE: this page needs an internet connection.
# =============================================================================

import streamlit as st
import pandas as pd
from utils.data_loader import load_companies
from utils.yfinance_loader import fetch_daily_data, close_series, rebase_to_100

st.set_page_config(page_title="Stock Price", layout="wide")

df = load_companies()

st.title("Stock Price")
st.write("Pick a company, then turn the S&P 500 comparison on or off.")

# -----------------------------------------------------------------------------
# 1. CHOOSE A COMPANY
# -----------------------------------------------------------------------------
# A friendly label like "AAPL - Apple Inc." is nicer in the menu than "AAPL".
df["label"] = df["symbol"] + " - " + df["company_name"]
choice = st.selectbox("Company", options=sorted(df["label"]))
symbol = choice.split(" - ")[0]  # keep just the ticker, e.g. "AAPL"

# -----------------------------------------------------------------------------
# 2. CHOOSE A DATE RANGE  (two date pickers, side by side)
# -----------------------------------------------------------------------------
col_start, col_end = st.columns(2)
start_date = col_start.date_input("Start date", value=pd.to_datetime("2026-01-01"))
end_date = col_end.date_input("End date", value=pd.to_datetime("2026-05-26"))

st.divider()

# -----------------------------------------------------------------------------
# 3. THE TWO BUTTONS  -  they switch "compare mode" on and off
# -----------------------------------------------------------------------------
# A button does not remember anything, so we store the mode in session_state.
if "compare" not in st.session_state:
    st.session_state.compare = False

# A "callback" is a small function that runs the instant a button is clicked,
# BEFORE the page re-runs. Using callbacks here means the buttons show the
# correct enabled / disabled look immediately.
def start_compare():
    st.session_state.compare = True

def stop_compare():
    st.session_state.compare = False

col_on, col_off = st.columns(2)

# "Compare S&P 500" is clickable only when we are NOT already comparing.
col_on.button(
    "Compare S&P 500",
    on_click=start_compare,
    disabled=st.session_state.compare,
    use_container_width=True,
)
# "Stop Compare" is clickable only when we ARE comparing.
col_off.button(
    "Stop Compare",
    on_click=stop_compare,
    disabled=not st.session_state.compare,
    use_container_width=True,
)

st.divider()


# -----------------------------------------------------------------------------
# 4. DOWNLOAD THE DATA AND DRAW THE CHART
# -----------------------------------------------------------------------------
if start_date >= end_date:
    st.error("The start date must be before the end date.")
else:
    try:
        # Always download the chosen company.
        stock = close_series(
            fetch_daily_data(
                symbol,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
            )
        )

        if st.session_state.compare:
            # ---- COMPARE MODE -------------------------------------------
            # Also download the S&P 500 (ticker "SPY") and normalise both.
            spy = close_series(
                fetch_daily_data(
                    "SPY",
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                )
            )
            chart = pd.DataFrame(
                {
                    symbol: rebase_to_100(stock),
                    "S&P 500": rebase_to_100(spy),
                }
            )
            st.subheader(f"{symbol} vs S&P 500 - normalised (start = 100)")
            st.line_chart(chart)
            st.caption(
                "Both lines start at 100, so the chart shows percentage "
                "performance. Click 'Stop Compare' to go back to the price."
            )
        else:
            # ---- NORMAL MODE --------------------------------------------
            # Just the closing price of the chosen company.
            st.subheader(f"Closing price - {symbol}")
            st.line_chart(stock)

    except Exception as error:
        st.error(f"Could not download the data: {error}")
