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
FILE_PATH = "fertilizer_import.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(FILE_PATH)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Sort by year
    df = df.sort_values("Year")

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
