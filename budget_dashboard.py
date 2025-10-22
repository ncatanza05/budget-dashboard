import streamlit as st
import pandas as pd
import time

# --- MOBILE STYLING ---
st.markdown("""
    <style>
        /* Reduce padding and margins */
        .block-container {
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
            max-width: 900px;
            margin: auto;
        }

        /* Make metric cards smaller */
        div[data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
        }

        /* Make metric labels smaller */
        div[data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }

        /* Shrink expander title font */
        div.streamlit-expanderHeader p {
            font-size: 1rem !important;
        }

        /* Compact table text */
        table {
            font-size: 0.8rem !important;
        }

        /* Reduce space under each table */
        .stDataFrame {
            margin-bottom: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)


# --- CONFIG ---
FILE_PATH = "Budget.xlsx"
SHEET_NAME = "DashboardData"
# --------------

st.set_page_config(page_title="Family Budget Dashboard", page_icon="💰", layout="centered")

@st.cache_data
def load_data():
    return pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME)

df = load_data()

# make sure numeric
df["Budget"] = pd.to_numeric(df["Budget"], errors="coerce").fillna(0)
df["Spent"] = pd.to_numeric(df["Spent"], errors="coerce").fillna(0)
df["Remaining"] = df["Budget"] - df["Spent"]

st.title("💰 Family Budget Dashboard")

total_budget = df["Budget"].sum()
total_spent = df["Spent"].sum()
total_remaining = df["Remaining"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Budget", f"${total_budget:,.0f}")
col2.metric("Total Spent", f"${total_spent:,.0f}")
col3.metric("Remaining", f"${total_remaining:,.0f}")

# --- GROUPED DISPLAY ---
st.divider()

# Set refresh interval in seconds (e.g., 300 = 5 minutes)
REFRESH_INTERVAL = 300

# Force refresh after each interval
st_autorefresh = st.empty()
if "last_refresh" not in st.session_state:
    st.session_state["last_refresh"] = time.time()

if time.time() - st.session_state["last_refresh"] > REFRESH_INTERVAL:
    st.session_state["last_refresh"] = time.time()
    st.rerun()

def color_remaining(val, budget):
    if budget == 0:
        return "color:gray;"
    pct_left = val / budget
    if val <= 0:
        color = "red"
    elif pct_left < 0.2:
        color = "orange"
    else:
        color = "green"
    return f"color:{color}; font-weight:bold;"

for category, group in df.groupby("Main Category"):
    with st.expander(f"📂 {category}", expanded=True):

        cat_budget = group["Budget"].sum()
        cat_spent = group["Spent"].sum()
        cat_remaining = group["Remaining"].sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("Subtotal Budget", f"${cat_budget:,.0f}")
        c2.metric("Subtotal Spent", f"${cat_spent:,.0f}")
        c3.metric("Subtotal Remaining", f"${cat_remaining:,.0f}")

        st.markdown("<hr style='margin:5px 0 10px 0;'>", unsafe_allow_html=True)

        def style_remaining(col):
            return [
                color_remaining(v, b)
                for v, b in zip(group["Remaining"], group["Budget"])
            ]

        styled = (
            group[["Subcategory", "Budget", "Spent", "Remaining"]]
            .style.format(
                {"Budget": "${:,.0f}", "Spent": "${:,.0f}", "Remaining": "${:,.0f}"}
            )
            .apply(style_remaining, subset=["Remaining"])
        )


        st.dataframe(styled, width="stretch", hide_index=True)
