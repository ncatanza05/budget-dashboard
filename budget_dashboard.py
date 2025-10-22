import streamlit as st
import pandas as pd
import time

# --- CONFIG ---
FILE_PATH = "Budget.xlsx"
SHEET_NAME = "DashboardData"
REFRESH_INTERVAL = 30  # seconds (5 minutes)
# --------------

# --- MOBILE STYLING ---
st.markdown("""
    <style>
        /* General container */
        .block-container {
            padding: 0.6rem 0.8rem !important;
            max-width: 900px;
            margin: auto;
        }

        /* Title */
        h1 {
            text-align: center !important;
            font-size: 1.4rem !important;
            margin-bottom: 0.3rem !important;
        }

        /* Metric cards (totals + subtotals) */
        div[data-testid="stMetric"] {
            text-align: center !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
            color: #444 !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 0.95rem !important;
            font-weight: 600 !important;
        }
        [data-testid="stHorizontalBlock"] > div {
            flex: 1 !important;
            min-width: 0 !important;
        }

        /* Expander header */
        div.streamlit-expanderHeader p {
            font-size: 0.9rem !important;
            font-weight: 600 !important;
        }

        /* Compact responsive centered table styling */
        .compact-table {
            width: 100% !important;
            border-collapse: collapse;
            table-layout: auto !important;
        }
        
        .compact-table th, .compact-table td {
            padding: 6px 4px;
            text-align: center;
            vertical-align: middle;
            font-size: 0.75rem;
            white-space: nowrap;
        }
        
        .compact-table th:first-child,
        .compact-table td:first-child {
            text-align: left;
            white-space: normal;
        }
        
        .compact-table tr:nth-child(even) {
            background-color: #f8f8f8;
        }

        hr {
            margin: 4px 0 !important;
            border: 0;
            border-top: 1px solid #ccc;
        }

        /* Force metric labels and values to center */
        [data-testid="stMetricValue"], 
        [data-testid="stMetricLabel"] {
            display: flex !important;
            justify-content: center !important;
            text-align: center !important;
            width: 100% !important;
        }
        
        [data-testid="stMetricValue"] > div {
            margin: 0 auto !important;
            text-align: center !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- AUTO PAGE REFRESH EVERY 30 SECONDS ---
st.markdown("""
    <script>
        function refreshPage() {
            window.location.reload();
        }
        setTimeout(refreshPage, 30000);  // 30 seconds = 30000 ms
    </script>
""", unsafe_allow_html=True)


# --- AUTO REFRESH ---
if "last_refresh" not in st.session_state:
    st.session_state["last_refresh"] = time.time()
if time.time() - st.session_state["last_refresh"] > REFRESH_INTERVAL:
    st.session_state["last_refresh"] = time.time()
    st.rerun()

# --- LOAD DATA ---
@st.cache_data(ttl=30, show_spinner=False)
def load_data():
    """Always reload Excel every 30s if changed on GitHub"""
    return pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME)

df = load_data()
df["Budget"] = pd.to_numeric(df["Budget"], errors="coerce").fillna(0)
df["Spent"] = pd.to_numeric(df["Spent"], errors="coerce").fillna(0)
df["Remaining"] = df["Budget"] - df["Spent"]

# --- PAGE TITLE ---
st.title("💰 Family Budget Dashboard")

# --- TOTALS ---
total_budget = df["Budget"].sum()
total_spent = df["Spent"].sum()
total_remaining = df["Remaining"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Budget", f"${total_budget:,.0f}")
col2.metric("Total Spent", f"${total_spent:,.0f}")
col3.metric("Total Remaining", f"${total_remaining:,.0f}")

st.divider()

# --- CATEGORY DISPLAY ---
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

        # --- SUBTOTALS ---
        cat_budget = group["Budget"].sum()
        cat_spent = group["Spent"].sum()
        cat_remaining = group["Remaining"].sum()

        # Centered subtotal metrics (no clipping)
        st.markdown("""
        <div style="display:flex;justify-content:space-around;flex-wrap:wrap;text-align:center;margin-bottom:4px;">
          <div style="flex:1;min-width:100px;">
            <div style="font-size:0.8rem;color:#555;">Subtotal Budget</div>
            <div style="font-weight:600;">${:,.0f}</div>
          </div>
          <div style="flex:1;min-width:100px;">
            <div style="font-size:0.8rem;color:#555;">Subtotal Spent</div>
            <div style="font-weight:600;">${:,.0f}</div>
          </div>
          <div style="flex:1;min-width:100px;">
            <div style="font-size:0.8rem;color:#555;">Subtotal Remaining</div>
            <div style="font-weight:600;">${:,.0f}</div>
          </div>
        </div>
        """.format(cat_budget, cat_spent, cat_remaining), unsafe_allow_html=True)

        st.markdown("<hr style='margin:5px 0 8px 0;'>", unsafe_allow_html=True)

        # --- STATIC FORMATTED TABLE (no index, full text) ---
        display_df = group[["Subcategory", "Budget", "Spent", "Remaining"]].copy()

        # Format currency
        for col in ["Budget", "Spent", "Remaining"]:
            display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")

        # Reset index to drop Excel row numbers
        display_df.reset_index(drop=True, inplace=True)

        # Render static table
        st.markdown(
            display_df.to_html(
                index=False,
                justify="center",
                border=0,
                col_space=70,
                escape=False,
                classes="compact-table"
            ),
            unsafe_allow_html=True
        )




