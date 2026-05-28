# pages/4_Matplotlib.py
# =============================================================================
# PAGE 4 - A MATPLOTLIB CHART
# =============================================================================
# So far the charts (bar_chart, scatter_chart, map) were Streamlit's own
# built-in charts. But Streamlit can also display a chart drawn with
# matplotlib - the classic Python plotting library - which gives you full
# control over colours, labels and styling.
#
# The recipe is always the same:
#   1. build a matplotlib figure     ->  fig, ax = plt.subplots()
#   2. draw on the axes              ->  ax.barh(...), ax.set_title(...), ...
#   3. hand the figure to Streamlit  ->  st.pyplot(fig)
#
# In a normal Python script you would finish with plt.show().
# Inside Streamlit you call st.pyplot(fig) instead.
# =============================================================================

import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from utils.data_loader import load_companies
from utils.plot_utils import billions_formatter, clean_spines

st.set_page_config(page_title="Matplotlib", page_icon="📊", layout="wide")

df = load_companies()

st.title("Page 4 - A Matplotlib Chart")
st.write(
    "A horizontal bar chart of the biggest companies, drawn with matplotlib "
    "and coloured by sector. The colour shows whether the largest companies "
    "are concentrated in one sector."
)

# A widget so the chart stays interactive, like the rest of the app.
how_many = st.slider("How many companies to show", min_value=5, max_value=30, value=20)


# -----------------------------------------------------------------------------
# 1. PREPARE THE DATA
# -----------------------------------------------------------------------------
# Take the N largest companies by market cap. Then sort ascending, so the
# biggest bar ends up at the TOP of the horizontal chart.
top = df.nlargest(how_many, "Market Cap (B$)").copy()
top = top.sort_values("Market Cap (B$)", ascending=True)

# Give every sector its own colour, taken from matplotlib's "tab20" palette.
sectors = list(top["sector"].unique())
cmap = plt.get_cmap("tab20", len(sectors))
sector_to_color = {sector: cmap(i) for i, sector in enumerate(sectors)}
# One colour per bar, looked up from the company's sector.
bar_colors = [sector_to_color[sector] for sector in top["sector"]]

# -----------------------------------------------------------------------------
# 2. BUILD THE MATPLOTLIB FIGURE
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))

# barh() draws HORIZONTAL bars - one bar per company.
bars = ax.barh(top["symbol"], top["Market Cap (B$)"], color=bar_colors)

ax.set_title(f"Top {how_many} companies by market capitalisation")
ax.set_xlabel("Market capitalisation")
ax.set_ylabel("Ticker")

# Show the X-axis numbers as "$300B" / "$1.5T" instead of raw values.
# A FuncFormatter changes only how the labels look, not the data itself.
ax.xaxis.set_major_formatter(FuncFormatter(billions_formatter))
ax.grid(axis="x", alpha=0.25)
clean_spines(ax)

# Leave a little empty space on the right so the bar labels are not clipped.
ax.set_xlim(0, top["Market Cap (B$)"].max() * 1.12)

# Write the value at the end of each bar.
for bar in bars:
    width = bar.get_width()
    ax.text(width, bar.get_y() + bar.get_height() / 2,
            f" {width:,.0f}B", va="center", fontsize=8)

# Build a legend that explains the sector colours.
legend_handles = [
    plt.Line2D([0], [0], marker="s", linestyle="", markersize=10,
               markerfacecolor=color, markeredgecolor=color, label=sector)
    for sector, color in sector_to_color.items()
]
ax.legend(handles=legend_handles, title="Sector", loc="lower right", fontsize=8)

fig.tight_layout()

# -----------------------------------------------------------------------------
# 3. HAND THE FIGURE TO STREAMLIT
# -----------------------------------------------------------------------------
st.pyplot(fig)

st.caption(
    "The key line is st.pyplot(fig): it takes any matplotlib figure and "
    "renders it inside the app."
)
