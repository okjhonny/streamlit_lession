# utils/plot_utils.py
# -----------------------------------------------------------------------------
# Small matplotlib helpers, kept here so any page that draws a matplotlib
# chart can reuse them with a single import:
#
#     from utils.plot_utils import billions_formatter, clean_spines
# -----------------------------------------------------------------------------


def billions_formatter(value, _pos):
    """Turn an axis number into a readable label: 1500 -> '$1.5T', 300 -> '$300B'."""
    if value >= 1000:
        return f"${value / 1000:.1f}T"
    return f"${value:.0f}B"


def clean_spines(ax):
    """Hide the top and right border lines of the plot, for a cleaner look."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
