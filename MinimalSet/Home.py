# Home.py
# =============================================================================
# STREAMLIT - MINIMUM SET (multi-page version)
# =============================================================================
# This is the app's entry point. In a multi-page Streamlit app:
#   - the file you launch becomes the Home page;
#   - every file inside the pages/ folder becomes an extra page in the
#     left-hand menu, automatically.
# To add a new page later, just drop a new file into pages/.
#
# HOW TO RUN
#   pip install -r requirements.txt
#   streamlit run Home.py
#
# GOLDEN RULE OF STREAMLIT
#   Every time the user touches a widget, Streamlit runs the page script
#   again from top to bottom. There are no "click handlers".
# =============================================================================

import streamlit as st
from utils.data_loader import load_companies

# st.set_page_config() must be the FIRST Streamlit command in the script.
st.set_page_config(page_title="Streamlit Minimum Set")

st.title("Streamlit - Minimal Dashboard ")
st.write(
    "A small, coherent example. Use the menu on the left to open each page."
)

# A short description of each page.
st.subheader("Pages")
st.write("**1 - Layout** : how to arrange the page in rows and columns.")
st.write("**2 - Explore** : filter the data and configure charts with widgets.")
st.write("**3 - Stock Price** : Yahoo Finance, plus buttons to compare with the S&P 500.")
st.write("**4 - Matplotlib** : display a classic matplotlib chart with st.pyplot.")

st.divider()
st.write(
    "A first look at the dataset....."
)

# A first look at the dataset shared by the pages.
df = load_companies()
st.subheader("The dataset")
st.write(f"The file contains **{len(df)} companies**. First 12 rows:")
st.dataframe(df.head(12), use_container_width=True, hide_index=True)

st.caption("Streamlit " + st.__version__)
