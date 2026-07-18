import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Thailand Fertilizer Import Dashboard",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Thailand Fertilizer Import Dashboard")

# -----------------------------
# Load Data
# -----------------------------
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "merged"
    / "fertilizer_import_master.xlsx"
)

@st.cache_data
def load_data():

    if not FILE_PATH.exists():
        st.error(f"Cannot find:\n{FILE_PATH}")
        st.stop()

    df = pd.read_excel(FILE_PATH)

    df.columns = df.columns.str.strip()

    df = df.sort_values("Year").reset_index(drop=True)

    return df

df = load_data()




# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Filter")

formula_list = sorted(df["Formula"].unique())

selected_formulas = st.sidebar.multiselect(
    "Select Formula",
    formula_list,
    default = [formula_list[0]]
)

if len(selected_formulas) >10:
    st.warning("Please select at most 5 formulas for comparison.")
    st.stop()
    
# -----------------------------
# Filter Data
# -----------------------------
filtered = df[df["Formula"].isin(selected_formulas)]

# Create complete Formula × Year grid
all_years = range(df["Year"].min(), df["Year"].max() + 1)

plot_df = (
    pd.MultiIndex.from_product(
        [selected_formulas, all_years],
        names=["Formula", "Year"]
    )
    .to_frame(index=False)
)

plot_df = plot_df.merge(
    filtered,
    on=["Formula", "Year"],
    how="left"
)

plot_df["Import_Volume_TON"] = plot_df["Import_Volume_TON"].fillna(0)
plot_df["Import_Value_THB"] = plot_df["Import_Value_THB"].fillna(0)
plot_df["AVG_price_THB_per_TON"] = plot_df["AVG_price_THB_per_TON"].fillna(0)




# -----------------------------
# Summary
# -----------------------------
st.write(", ".join(selected_formulas))

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Import Volume (TON)",
        f"{filtered['Import_Volume_TON'].sum():,.0f}"
    )

with col2:
    st.metric(
        "Total Import Value (THB)",
        f"{filtered['Import_Value_THB'].sum():,.0f}"
    )

with col3:
    st.metric(
        "Average Price (THB/TON)",
        f"{filtered['AVG_price_THB_per_TON'].mean():,.0f}"
    )

st.divider()

# =============================
# Volume Trend
# =============================
fig_volume = px.line(
    plot_df,
    x="Year",
    y="Import_Volume_TON",
    markers=True,
    title="Import Volume Comparison",
    color = "Formula"
    
)

fig_volume.update_layout(
    xaxis_title="Year",
    yaxis_title="Ton",
    height=450
)

fig_volume.update_traces(
    hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Volume: %{y:,.2f} TON<extra></extra>"
)

st.plotly_chart(fig_volume, use_container_width=True)

# =============================
# Import Value Trend
# =============================
fig_value = px.line(
    plot_df,
    x="Year",
    y="Import_Value_THB",
    markers=True,
    title = "Import Value Comparison",
    color = "Formula"
)

fig_value.update_layout(
    xaxis_title="Year",
    yaxis_title="THB",
    height=450
)

fig_value.update_traces(
    hovertemplate="<b>Year:</b> %{x}<br><b>Value:</b> %{y:,.2f} THB<extra></extra>"
)

st.plotly_chart(fig_value, use_container_width=True)

# =============================
# Average Price Trend
# =============================
fig_price = px.line(
    plot_df,
    x="Year",
    y="AVG_price_THB_per_TON",
    markers=True,
    title="Average Price Comparision",
    color = "Formula"
)

fig_price.update_layout(
    xaxis_title="Year",
    yaxis_title="THB / TON",
    height=450
)

fig_price.update_traces(
    hovertemplate="<b>Year:</b> %{x}<br><b>Price:</b> %{y:,.2f} THB / TON<extra></extra>"
)

st.plotly_chart(fig_price, use_container_width=True)

# -----------------------------
# Data Table
# -----------------------------
st.subheader("Import Volume Table (TON)")

volume_table = plot_df.pivot(
    index="Year",
    columns="Formula",
    values="Import_Volume_TON"
).fillna(0)

st.dataframe(
    volume_table.style.format("{:,.0f}"),
    use_container_width=True
)


# ==========================================================
# Top Imported Fertilizer Formulas
# ==========================================================

st.divider()
st.header("🏆 Top Imported Fertilizer Formulas")


# -----------------------------
# Controls
# -----------------------------


col1, col2 = st.columns(2)

with col1:

    analysis_period = st.selectbox(
        "Analysis Period",
        ["All Years"] + sorted(df["Year"].unique(), reverse=True)
    )

with col2:

    top_n = st.slider(
        "Top N",
        min_value=5,
        max_value=30,
        value=10
    )

# -----------------------------
# Filter by Year
# -----------------------------
if analysis_period == "All Years":

    top_df = (
        df.groupby("Formula", as_index=False)
        .agg({
            "Import_Volume_TON": "sum",
            "Import_Value_THB": "sum"
        })
    )

else:

    top_df = df[df["Year"] == analysis_period].copy()

# Make sure Formula is text
top_df["Formula"] = top_df["Formula"].astype(str)

# -----------------------------
# Prepare Data
# -----------------------------
top_volume = (
    top_df
    .sort_values(by="Import_Volume_TON", ascending=False)
    .head(top_n)
)

top_value = (
    top_df
    .sort_values(by="Import_Value_THB", ascending=False)
    .head(top_n)
)

# -----------------------------
# Charts
# -----------------------------
left, right = st.columns(2)

# ======================================================
# Top Import Volume
# ======================================================

with left:

    fig_top_volume = px.bar(
        data_frame=top_volume,
        x="Import_Volume_TON",
        y="Formula",
        orientation="h",
        title=f"Top {top_n} Import Volume ({analysis_period})"
    )

    fig_top_volume.update_layout(
        height=600,
        yaxis_title="Formula",
        xaxis_title="Import Volume (TON)",
        yaxis=dict(autorange="reversed")
    )

    fig_top_volume.update_traces(
        hovertemplate="<b>%{y}</b><br>Volume: %{x:,.0f} TON<extra></extra>"
    )

    fig_top_volume.update_yaxes(type="category")

    st.plotly_chart(fig_top_volume, use_container_width=True)

# ======================================================
# Top Import Value
# ======================================================

with right:

    fig_top_value = px.bar(
        data_frame=top_value,
        x="Import_Value_THB",
        y="Formula",
        orientation="h",
        title=f"Top {top_n} Import Value ({analysis_period})"
    )

    fig_top_value.update_layout(
        height=600,
        yaxis_title="Formula",
        xaxis_title="Import Value (THB)",
        yaxis=dict(autorange="reversed")
    )

    fig_top_value.update_traces(
        hovertemplate="<b>%{y}</b><br>Value: %{x:,.0f} THB<extra></extra>"
    )

    fig_top_value.update_yaxes(type="category")

    st.plotly_chart(fig_top_value, use_container_width=True)




st.divider()
st.header("📊 Market Share Analysis")

# ----------------------------------------
# Market Share Data
# ----------------------------------------

market_df = top_df.copy()

market_df["Volume Share (%)"] = (
    market_df["Import_Volume_TON"]
    / market_df["Import_Volume_TON"].sum()
    * 100
)

market_df["Value Share (%)"] = (
    market_df["Import_Value_THB"]
    / market_df["Import_Value_THB"].sum()
    * 100
)

market_df = market_df.sort_values(
    "Volume Share (%)",
    ascending=False
).head(top_n)

left, right = st.columns(2)

with left:

    fig_market_volume = px.pie(
        market_df,
        names="Formula",
        values="Volume Share (%)",
        title=f"Top {top_n} Market Share by Volume"
    )

    fig_market_volume.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>%{percent}<br>Volume: %{value:.2f}%<extra></extra>"
    )

    st.plotly_chart(
        fig_market_volume,
        use_container_width=True
    )


with right:

    fig_market_value = px.pie(
        market_df,
        names="Formula",
        values="Value Share (%)",
        title=f"Top {top_n} Market Share by Value"
    )

    fig_market_value.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>%{percent}<br>Value: %{value:.2f}%<extra></extra>"
    )

    st.plotly_chart(
        fig_market_value,
        use_container_width=True
    )


# -----------------------------
# Year-over-Year-Growth
# -----------------------------
st.divider()
st.header("📈 Year-over-Year Growth")

# -----------------------------
# Controls
# -----------------------------
col1, col2 = st.columns(2)

with col1:

    yoy_year = st.selectbox(
        "Compare Year",
        sorted(df["Year"].unique())[1:],      # starts from second year
        index=len(sorted(df["Year"].unique()))-2
    )

with col2:

    growth_metric = st.selectbox(
    "Metric",
    [
        "Import Volume",
        "Import Value",
        "Average Price per TON"
    ]
)

# -----------------------------
# Previous Year
# -----------------------------
previous_year = yoy_year - 1

# -----------------------------
# Get data
# -----------------------------
current_df = df[df["Year"] == yoy_year]

previous_df = df[df["Year"] == previous_year]

# -----------------------------
# Merge
# -----------------------------
growth_df = current_df.merge(
    previous_df,
    on="Formula",
    suffixes=("_current", "_previous"),
    how="outer"
)


# -----------------------------
# Replacing Missing Value
# -----------------------------
growth_df = growth_df.fillna(0)


# -----------------------------
# Calculated Growth
# -----------------------------
if growth_metric == "Import Volume":

    growth_df["Growth (%)"] = np.where(
        growth_df["Import_Volume_TON_previous"] > 0,
        (
            (growth_df["Import_Volume_TON_current"]
            - growth_df["Import_Volume_TON_previous"])
            / growth_df["Import_Volume_TON_previous"]
            * 100
        ),
        np.nan
    )

elif growth_metric == "Import Value":

    growth_df["Growth (%)"] = np.where(
        growth_df["Import_Value_THB_previous"] > 0,
        (
            (growth_df["Import_Value_THB_current"]
            - growth_df["Import_Value_THB_previous"])
            / growth_df["Import_Value_THB_previous"]
            * 100
        ),
        np.nan
    )

else:

    growth_df["Growth (%)"] = np.where(
        growth_df["AVG_price_THB_per_TON_previous"] > 0,
        (
            (growth_df["AVG_price_THB_per_TON_current"]
            - growth_df["AVG_price_THB_per_TON_previous"])
            / growth_df["AVG_price_THB_per_TON_previous"]
            * 100
        ),
        np.nan
    )

# ---------------------------------------------------
# Filter out very small formulas (ADD THIS HERE)
# ---------------------------------------------------
growth_df = growth_df[
    growth_df["Import_Volume_TON_previous"] >= 1000
]

# -----------------------------
# Sort
# -----------------------------
growth_df = growth_df.sort_values(
    "Growth (%)",
    ascending=False
)

# -----------------------------
# Split into Growth and Decline
# -----------------------------
growth_positive = growth_df[growth_df["Growth (%)"] > 0]

growth_negative = growth_df[growth_df["Growth (%)"] < 0]

# -----------------------------
# Charts
# -----------------------------
left, right = st.columns(2)

with left:

    fig_growth = px.bar(
        growth_positive.head(10),
        x="Growth (%)",
        y="Formula",
        orientation="h",
        title=f"Top 10 Growth ({previous_year} → {yoy_year})",
        text="Growth (%)"
    )

    fig_growth.update_layout(
        height=600,
        yaxis=dict(autorange="reversed")
    )

    fig_growth.update_traces(
        texttemplate="%{text:.1f}%",
        hovertemplate="<b>%{y}</b><br>%{x:.2f}%<extra></extra>"
    )

    fig_growth.update_yaxes(type="category")

    st.plotly_chart(
        fig_growth,
        use_container_width=True
    )


with right:

    fig_decline = px.bar(
        growth_df.tail(10),
        x="Growth (%)",
        y="Formula",
        orientation="h",
        title=f"Top 10 Decline ({previous_year} → {yoy_year})",
        text="Growth (%)"
    )

    fig_decline.update_layout(
        height=600
    )

    fig_decline.update_traces(
        texttemplate="%{text:.1f}%",
        hovertemplate="<b>%{y}</b><br>%{x:.2f}%<extra></extra>"
    )
    
    fig_decline.update_yaxes(type="category")

    st.plotly_chart(
        fig_decline,
        use_container_width=True
    )


# -----------------------------
# Table
# -----------------------------

st.subheader("Growth Table")

show_table = growth_df[
    [
        "Formula",
        "Growth (%)"
    ]
].copy()

show_table["Growth (%)"] = show_table["Growth (%)"].round(2)

st.dataframe(
    show_table,
    use_container_width=True,
    hide_index=True
)
