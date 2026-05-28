# utils/data_loader.py
# -----------------------------------------------------------------------------
# Helper functions that load the companies dataset.
# They live in utils/ so every page can reuse them without repeating the code.
#
# @st.cache_data -> Streamlit re-runs the whole script on every interaction;
# this decorator makes the work below happen only once, then reused.
# -----------------------------------------------------------------------------

import pandas as pd
import streamlit as st


@st.cache_data
def load_companies():
    """Load the companies CSV and keep a few easy-to-read columns."""
    df = pd.read_csv("./data/Symbols_info_extended.csv")

    # Keep a small subset of columns so the tables stay readable.
    columns = ["symbol", "company_name", "sector", "industry",
               "current_price", "market_cap", "dividend_yield"]
    df = df[columns]

    # Turn text into numbers; invalid values become NaN (Not a Number).
    df["current_price"] = pd.to_numeric(df["current_price"], errors="coerce")
    df["market_cap"] = pd.to_numeric(df["market_cap"], errors="coerce")
    df["dividend_yield"] = pd.to_numeric(df["dividend_yield"], errors="coerce")

    # Drop rows missing the fields we rely on.
    df = df.dropna(subset=["sector", "current_price", "market_cap"])

    # A missing dividend yield simply means the company pays no dividend -> 0.
    df["dividend_yield"] = df["dividend_yield"].fillna(0)

    # Market cap is a huge number of dollars; in billions it is readable.
    df["Market Cap (B$)"] = (df["market_cap"] / 1_000_000_000).round(1)

    return df


# Approximate geographic centre (latitude, longitude) of every country that
# appears in the dataset. The Layout page uses this to place dots on a map.
COUNTRY_COORDS = {
    "Australia": (-25.27, 133.78),
    "Bahamas": (24.25, -76.00),
    "Bermuda": (32.32, -64.75),
    "Brazil": (-14.24, -51.93),
    "British Virgin Islands": (18.42, -64.64),
    "Canada": (56.13, -106.35),
    "Cayman Islands": (19.31, -81.25),
    "Chile": (-35.68, -71.54),
    "China": (35.86, 104.20),
    "Colombia": (4.57, -74.30),
    "Costa Rica": (9.75, -83.75),
    "Cyprus": (35.13, 33.43),
    "Egypt": (26.82, 30.80),
    "Finland": (61.92, 25.75),
    "France": (46.23, 2.21),
    "Germany": (51.17, 10.45),
    "Greece": (39.07, 21.82),
    "Guernsey": (49.47, -2.59),
    "Hong Kong": (22.32, 114.17),
    "India": (20.59, 78.96),
    "Ireland": (53.41, -8.24),
    "Israel": (31.05, 34.85),
    "Italy": (41.87, 12.57),
    "Jersey": (49.21, -2.13),
    "Luxembourg": (49.82, 6.13),
    "Mexico": (23.63, -102.55),
    "Monaco": (43.74, 7.42),
    "Netherlands": (52.13, 5.29),
    "Norway": (60.47, 8.47),
    "Panama": (8.54, -80.78),
    "Peru": (-9.19, -75.02),
    "Singapore": (1.35, 103.82),
    "South Korea": (35.91, 127.77),
    "Spain": (40.46, -3.75),
    "Sweden": (60.13, 18.64),
    "Switzerland": (46.82, 8.23),
    "Taiwan": (23.70, 120.96),
    "Thailand": (15.87, 100.99),
    "Turkey": (38.96, 35.24),
    "United Kingdom": (55.38, -3.44),
    "United States": (37.09, -95.71),
    "Uruguay": (-32.52, -55.77),
}


# A few company-country names differ from the official ISO 3166 names used in
# country.csv. This maps them so the region merge finds a match for every one.
COUNTRY_NAME_FIXES = {
    "British Virgin Islands": "Virgin Islands (British)",
    "Netherlands": "Netherlands, Kingdom of the",
    "South Korea": "Korea, Republic of",
    "Taiwan": "Taiwan, Province of China",
    "Turkey": "Türkiye",
    "United Kingdom": "United Kingdom of Great Britain and Northern Ireland",
    "United States": "United States of America",
}

# One colour per continent-level region, used to colour the map dots.
REGION_COLORS = {
    "Americas": "#1f77b4",  # blue
    "Europe": "#2ca02c",    # green
    "Asia": "#ff7f0e",      # orange
    "Oceania": "#9467bd",   # purple
    "Africa": "#d62728",    # red
}


@st.cache_data
def load_companies_by_country():
    """
    Count the companies per country, attach map coordinates and a region colour.

    Returns a DataFrame with one row per country and the columns:
        country, companies, lat, lon, size, region, color
    st.map() needs 'lat'/'lon'; 'size' is the dot radius; 'color' is the
    region colour so dots are grouped by continent on the map.
    """
    df = pd.read_csv("data/Symbols_info_extended.csv")
    df = df.dropna(subset=["country"])

    # How many companies belong to each country.
    counts = df["country"].value_counts().reset_index()
    counts.columns = ["country", "companies"]

    # Attach latitude / longitude from the table above.
    counts["lat"] = counts["country"].map(lambda c: COUNTRY_COORDS.get(c, (None, None))[0])
    counts["lon"] = counts["country"].map(lambda c: COUNTRY_COORDS.get(c, (None, None))[1])
    counts = counts.dropna(subset=["lat", "lon"])

    # st.map draws a circle per row; 'size' is its radius in metres.
    # We use a square-root scale so small countries stay visible while the
    # USA (by far the largest) does not cover the whole map.
    counts["size"] = (counts["companies"] ** 0.5) * 15000

    # Add a 'region' column by merging with the ISO 3166 list in country.csv,
    # which tags every country with its continent-level region.
    regions = pd.read_csv("data/country.csv")[["name", "region"]]
    counts["iso_name"] = counts["country"].replace(COUNTRY_NAME_FIXES)
    counts = counts.merge(regions, left_on="iso_name", right_on="name", how="left")

    # Taiwan has no region in the ISO file; it belongs to Asia.
    counts.loc[counts["country"] == "Taiwan", "region"] = "Asia"

    # Give every dot the colour of its region.
    counts["color"] = counts["region"].map(REGION_COLORS)

    return counts[["country", "companies", "lat", "lon", "size", "region", "color"]]
