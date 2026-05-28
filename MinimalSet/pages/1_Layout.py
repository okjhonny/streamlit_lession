# pages/1_Layout.py
# =============================================================================
# PAGE 1 - LAYOUT
# =============================================================================
# By default Streamlit stacks everything vertically. To organise the page we
# use two tools:
#
#   st.container()  -> an (invisible) box that groups elements. One per "ROW".
#   st.columns(n)   -> splits a row into n side-by-side COLUMNS.
#
# This page builds a layout with TWO ROWS:
#   ROW 1  ->  split into TWO COLUMNS
#              left  : two key numbers (metrics)
#              right : a histogram of companies per sector
#   ROW 2  ->  one full-width element: a map of the companies by country
# =============================================================================

import streamlit as st
from utils.data_loader import load_companies, load_companies_by_country, REGION_COLORS

st.set_page_config(page_title="Layout", layout="wide")

df = load_companies()

st.title("Page 1 - Layout")
st.write("A layout with two rows. The first row is split into two columns.")

st.divider()

# -----------------------------------------------------------------------------
# ROW 1  -  one container split into TWO COLUMNS
# -----------------------------------------------------------------------------
# st.container() creates the row; calling .columns(2) on it splits that row
# into two equal columns placed side by side.
row1 = st.container()
col_numbers, col_chart = row1.columns(2)

# --- ROW 1, COLUMN 1: two key numbers -------------------------------------
# st.metric() shows one big number. Two calls = two numbers, stacked.
col_numbers.subheader("Key numbers")
col_numbers.metric("Total sectors", df["sector"].nunique())
col_numbers.metric("Total industries", df["industry"].nunique())

# --- ROW 1, COLUMN 2: a histogram -----------------------------------------
# value_counts() counts how many companies fall in each sector.
# st.bar_chart() then draws one bar per sector (a histogram of companies).
col_chart.subheader("Companies per sector")
companies_per_sector = df["sector"].value_counts()
col_chart.bar_chart(companies_per_sector)

st.divider()

# -----------------------------------------------------------------------------
# ROW 2  -  a second container, used at full width: a MAP
# -----------------------------------------------------------------------------
# st.map() draws points on a real map. It needs a DataFrame with a 'lat' and
# a 'lon' column. load_companies_by_country() prepares exactly that, plus a
# 'size' column (dot radius = number of companies) and a 'color' column so
# each dot is coloured by the continent-level region it belongs to.
row2 = st.container()
row2.subheader("Where the companies are based")
row2.write("Each circle is a country - bigger means more companies, colour shows the region.")

country_data = load_companies_by_country()
row2.map(country_data, size="size", color="color", use_container_width=True)

# st.map has no built-in legend, so we draw a small one from the same colours.
legend = "&nbsp;&nbsp;".join(
    f"<span style='color:{color}; font-size:1.3em'>&#9679;</span> {region}"
    for region, color in REGION_COLORS.items()
)
row2.markdown(legend, unsafe_allow_html=True)
