# pages/2_Explore.py
# =============================================================================
# PAGE 2 - EXPLORE COMPANIES
# =============================================================================
# This page is all about CHOOSING. The user picks filters and chart options
# with widgets, and the page reacts to every change.
#
# Widgets used here:
#   st.selectbox -> pick one option from a menu
#   st.radio     -> pick one option, all shown at once
#   st.slider    -> pick a number
#
# Remember the golden rule: every time a widget changes, Streamlit runs this
# whole script again - so the charts below always match the current choices.
# =============================================================================

import streamlit as st
from utils.data_loader import load_companies

# layout="wide" uses the full browser width - good for a dashboard.
st.set_page_config(page_title="Explore", layout="wide")

df = load_companies()

st.title("Page 2 - Explore Companies")
st.write("Pick filters and chart options; everything updates as you change them.")

st.divider()

# -----------------------------------------------------------------------------
# 1. FILTERS  -  two menus, where the second depends on the first
# -----------------------------------------------------------------------------
st.subheader("Select Sector and Industry")

filter_left, filter_right = st.columns(2)

# First menu: choose a sector.
sector = filter_left.selectbox("Sector", options=sorted(df["sector"].unique()))

# Second menu: the list of industries depends on the sector chosen above.
industries = sorted(df[df["sector"] == sector]["industry"].dropna().unique())
industry = filter_right.selectbox("Industry", options=industries)

# KEY POINT HERE: Keep only the companies that match both choices.
data = df[(df["sector"] == sector) & (df["industry"] == industry)]

# -----------------------------------------------------------------------------
# 2. KPI METRICS  -  three summary numbers, side by side
# -----------------------------------------------------------------------------
st.subheader("Key numbers")

k1, k2, k3 = st.columns(3) #with border

k1.metric("Companies", len(data))
k2.metric("Average price", f"${data['current_price'].mean():,.2f}")
k3.metric("Average market cap", f"${data['Market Cap (B$)'].mean():,.1f} B")


# Dati dell'intero settore (indipendente dall'industry scelta)
sector_data = df[df["sector"] == sector]

# --- Valori industry (già filtrati) ---
n_industry        = len(data)
avg_price_ind     = data["current_price"].mean()
avg_cap_ind       = data["Market Cap (B$)"].mean()

# --- Baseline settore ---
avg_companies_per_industry = sector_data.groupby("industry").size().mean()
avg_price_sec     = sector_data["current_price"].mean()
avg_cap_sec       = sector_data["Market Cap (B$)"].mean()

k1a, k2a, k3a = st.columns(3, border=True) #with border

k1a.metric(
    label="Companies",
    value=n_industry,
    delta=f"{n_industry - avg_companies_per_industry:,.1f} vs sector avg",
    delta_color="normal",
    help=f"Avg per industry in sector: {avg_companies_per_industry:,.1f}",
)

k2a.metric(
    label="Avg Price",
    value=f"${avg_price_ind:,.2f}",
    delta=f"${avg_price_ind - avg_price_sec:,.2f} vs sector",
    delta_color="normal",
    help=f"Sector avg: ${avg_price_sec:,.2f}",
)

k3a.metric(
    label="Avg Market Cap",
    value=f"${avg_cap_ind:,.1f} B",
    delta=f"${avg_cap_ind - avg_cap_sec:,.1f} B vs sector",
    delta_color="normal",
    help=f"Sector avg: ${avg_cap_sec:,.1f} B",
)



# -----------------------------------------------------------------------------
# 3. BAR CHART  -  the user chooses WHICH metric to chart
# -----------------------------------------------------------------------------
st.subheader("Top companies")

# A dictionary maps a nice label (shown to the user) to the real column name.
metric_choices = {
    "Market cap (B$)": "Market Cap (B$)",
    "Price ($)": "current_price",
    "Dividend yield (%)": "dividend_yield",
}

# st.radio returns the label the user picked; we look up the column for it.
chosen_label = st.radio(
    "Which metric to chart",
    options=list(metric_choices.keys()),
    horizontal=True,
)
chosen_column = metric_choices[chosen_label]

# st.slider chooses how many companies to show. A slider needs min < max, so
# we only show it when there are at least 2 companies to choose from.
if len(data) >= 2:
    how_many = st.slider("How many companies", 1, len(data), min(10, len(data)))
else:
    how_many = len(data)

# Sort by the chosen metric, keep the top N, and draw the bar chart.
top = data.sort_values(chosen_column, ascending=False).head(how_many)
st.bar_chart(top.set_index("symbol")[chosen_column])

# -----------------------------------------------------------------------------
# 4. SCATTER CHART  -  two range sliders + a third metric for the dot size
# -----------------------------------------------------------------------------
st.subheader("Price vs market cap")
st.write(
    "A scatter chart uses THREE metrics at once: the X axis, the Y axis, and "
    "the dot SIZE. The two range sliders below let you zoom in on part of the "
    "data."
)


# A small helper: a range slider returns a (low, high) pair when its default
# value is a tuple. A slider needs min < max, so when the selected industry
# has a single value we skip the slider to avoid an error.
def range_slider(label, column, where):
    low = float(data[column].min())
    high = float(data[column].max())
    if high > low:
        return where.slider(label, low, high, (low, high))
    where.caption(f"{label}: only one value available")
    return (low, high)


slider_left, slider_right = st.columns(2)
# Range slider 1 -> filters the X axis (price).
price_range = range_slider("Price ($) range", "current_price", slider_left)
# Range slider 2 -> filters the Y axis (market cap).
cap_range = range_slider("Market cap (B$) range", "Market Cap (B$)", slider_right)

# Keep only the companies whose values fall inside BOTH ranges.
scatter_data = data[
    data["current_price"].between(price_range[0], price_range[1])
    & data["Market Cap (B$)"].between(cap_range[0], cap_range[1])
]

if scatter_data.empty:
    st.info("No companies fall inside the selected ranges - widen the sliders.")
else:
    # x  -> first metric  (price)
    # y  -> second metric (market cap)
    # size -> THIRD metric (dividend yield): a bigger dot = a higher yield.
    st.scatter_chart(
        scatter_data,
        x="current_price",
        y="Market Cap (B$)",
        size="dividend_yield",
    )
    st.caption("Each dot is a company. Bigger dot = higher dividend yield.")


