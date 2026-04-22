import copy
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: #0d0f14;
    color: #e8eaf0;
}
section[data-testid="stSidebar"] {
    background: #13161e !important;
    border-right: 1px solid #1e2330;
}
section[data-testid="stSidebar"] * {
    color: #c8ccd8 !important;
}
[data-testid="metric-container"] {
    background: #13161e;
    border: 1px solid #1e2330;
    border-radius: 12px;
    padding: 16px 20px;
    transition: border-color 0.2s;
}
[data-testid="metric-container"]:hover {
    border-color: #3d7aff;
}
[data-testid="metric-container"] label {
    color: #7a7f94 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-family: 'Space Mono', monospace !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e8eaf0 !important;
    font-size: 1.6rem !important;
    font-weight: 600;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
}
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #3d7aff;
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e2330;
}
.main-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: #e8eaf0;
    letter-spacing: -0.01em;
}
.main-subtitle {
    font-family: 'DM Sans', sans-serif;
    color: #5a5f74;
    font-size: 0.9rem;
    margin-top: 2px;
}
.element-container { background: transparent; }
hr { border-color: #1e2330 !important; margin: 8px 0 !important; }
.stSelectbox > div > div {
    background: #13161e !important;
    border-color: #1e2330 !important;
    color: #e8eaf0 !important;
}
.stMultiSelect > div > div {
    background: #13161e !important;
    border-color: #1e2330 !important;
}
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #1e2330; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── Color Palette ────────────────────────────────────────────────────────────
COLORS = {
    "Shopping":      "#3d7aff",
    "Bills":         "#ff6b6b",
    "Food":          "#ffd166",
    "Health":        "#06d6a0",
    "Transport":     "#a78bfa",
    "Entertainment": "#f97316",
}
METHOD_COLORS = ["#3d7aff", "#06d6a0", "#ffd166"]
CHART_BG   = "#13161e"
GRID_COLOR = "#1e2330"
TEXT_COLOR = "#c8ccd8"

# FIX 1: Base layout dict — never mutate this directly; always deepcopy first
_BASE_LAYOUT = dict(
    paper_bgcolor=CHART_BG,
    plot_bgcolor=CHART_BG,
    font=dict(family="DM Sans", color=TEXT_COLOR, size=12),
    margin=dict(l=16, r=16, t=36, b=16),
    xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(size=11)),
    yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(size=11)),
)

def base_layout(**overrides):
    """Return a fresh deep-copy of the base layout with optional overrides merged in."""
    layout = copy.deepcopy(_BASE_LAYOUT)
    layout.update(overrides)
    return layout

# ─── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("finance_year.csv", parse_dates=["Date"])
    df["Month"]     = df["Date"].dt.to_period("M").astype(str)
    df["MonthName"] = df["Date"].dt.strftime("%b %Y")
    df["Week"]      = df["Date"].dt.isocalendar().week.astype(int)
    df["DayOfWeek"] = df["Date"].dt.day_name()
    return df

df = load_data()

# ─── Sidebar Filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title">Filters</div>', unsafe_allow_html=True)

    months_sorted = sorted(df["Month"].unique())
    month_range = st.select_slider(
        "Date Range",
        options=months_sorted,
        value=(months_sorted[0], months_sorted[-1])
    )

    all_cats = sorted(df["Category"].unique())
    selected_cats = st.multiselect("Categories", all_cats, default=all_cats)

    all_methods = sorted(df["Payment_Method"].unique())
    selected_methods = st.multiselect("Payment Methods", all_methods, default=all_methods)

    st.markdown("---")
    st.markdown('<div class="section-title">Chart Style</div>', unsafe_allow_html=True)
    category_chart_type = st.radio("Category View", ["Bar Chart", "Pie Chart"], horizontal=True)

# ─── Filter Data ──────────────────────────────────────────────────────────────
mask = (
    (df["Month"] >= month_range[0]) &
    (df["Month"] <= month_range[1]) &
    (df["Category"].isin(selected_cats)) &
    (df["Payment_Method"].isin(selected_methods))
)
filtered = df[mask].copy()

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 24px;">
  <div class="main-title">Personal Finance Dashboard</div>
  <div class="main-subtitle">Spending analysis · 2025</div>
</div>
""", unsafe_allow_html=True)

# ─── KPI Metrics ──────────────────────────────────────────────────────────────
total        = filtered["Amount"].sum()
avg_monthly  = filtered.groupby("Month")["Amount"].sum().mean() if not filtered.empty else 0
top_cat      = filtered.groupby("Category")["Amount"].sum().idxmax() if not filtered.empty else "—"
top_cat_pct  = (filtered[filtered["Category"] == top_cat]["Amount"].sum() / total * 100) if total > 0 else 0
transactions = len(filtered)
avg_tx       = filtered["Amount"].mean() if transactions > 0 else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Spending",  f"{total:,.0f} EGP")
c2.metric("Monthly Average", f"{avg_monthly:,.0f} EGP")
c3.metric("Top Category",    top_cat, f"{top_cat_pct:.1f}% of total")
c4.metric("Transactions",    f"{transactions:,}", f"avg {avg_tx:,.0f} EGP each")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Row 1: Monthly Trend + Category ─────────────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown('<div class="section-title">Monthly Spending Trend</div>', unsafe_allow_html=True)

    # FIX 2: removed unused `monthly` variable — using monthly_total directly
    monthly_total = (
        filtered.groupby(["Month", "MonthName"])["Amount"]
        .sum().reset_index().sort_values("Month")
    )

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly_total["MonthName"],
        y=monthly_total["Amount"],
        fill="tozeroy",
        fillcolor="rgba(61,122,255,0.08)",
        line=dict(color="#3d7aff", width=2.5),
        mode="lines+markers",
        marker=dict(size=6, color="#3d7aff", line=dict(width=2, color="#0d0f14")),
        name="Total",
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} EGP<extra></extra>"
    ))
    fig_trend.update_layout(
        **base_layout(height=280, showlegend=False, yaxis_tickformat=",")
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.markdown('<div class="section-title">By Category</div>', unsafe_allow_html=True)

    cat_totals  = filtered.groupby("Category")["Amount"].sum().reset_index()
    cat_totals  = cat_totals.sort_values("Amount", ascending=False)
    cat_colors  = [COLORS.get(c, "#3d7aff") for c in cat_totals["Category"]]

    if category_chart_type == "Bar Chart":
        fig_cat = go.Figure(go.Bar(
            x=cat_totals["Category"],
            y=cat_totals["Amount"],
            marker_color=cat_colors,
            hovertemplate="<b>%{x}</b><br>%{y:,.0f} EGP<extra></extra>",
        ))
        fig_cat.update_layout(
            **base_layout(height=280, showlegend=False, yaxis_tickformat=",")
        )
    else:
        fig_cat = go.Figure(go.Pie(
            labels=cat_totals["Category"],
            values=cat_totals["Amount"],
            marker_colors=cat_colors,
            hole=0.5,
            textinfo="label+percent",
            textfont=dict(size=11, color=TEXT_COLOR),
            hovertemplate="<b>%{label}</b><br>%{value:,.0f} EGP (%{percent})<extra></extra>",
        ))
        fig_cat.update_layout(
            paper_bgcolor=CHART_BG,
            plot_bgcolor=CHART_BG,
            font=dict(family="DM Sans", color=TEXT_COLOR),
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=True,
            legend=dict(bgcolor=CHART_BG, font=dict(size=10), orientation="v", x=1.05)
        )

    st.plotly_chart(fig_cat, use_container_width=True)

# ─── Row 2: Stacked Monthly + Payment Method ─────────────────────────────────
col3, col4 = st.columns([3, 2])

with col3:
    st.markdown('<div class="section-title">Monthly Breakdown by Category</div>', unsafe_allow_html=True)

    monthly_cat = (
        filtered.groupby(["Month", "Category"])["Amount"]
        .sum().reset_index().sort_values("Month")
    )

    fig_stack = go.Figure()
    for cat in all_cats:
        sub = monthly_cat[monthly_cat["Category"] == cat]
        fig_stack.add_trace(go.Bar(
            x=sub["Month"],
            y=sub["Amount"],
            name=cat,
            marker_color=COLORS.get(cat, "#888"),
            hovertemplate=f"<b>{cat}</b><br>%{{y:,.0f}} EGP<extra></extra>",
        ))

    fig_stack.update_layout(
        **base_layout(
            height=280,
            barmode="stack",
            yaxis_tickformat=",",
            legend=dict(
                bgcolor=CHART_BG,
                font=dict(size=10),
                orientation="h",
                y=-0.25
            ),
        )
    )
    st.plotly_chart(fig_stack, use_container_width=True)

with col4:
    st.markdown('<div class="section-title">Payment Methods</div>', unsafe_allow_html=True)

    method_totals = filtered.groupby("Payment_Method")["Amount"].sum().reset_index()

    fig_method = go.Figure(go.Bar(
        x=method_totals["Amount"],
        y=method_totals["Payment_Method"],
        orientation="h",
        marker_color=METHOD_COLORS[:len(method_totals)],
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} EGP<extra></extra>",
        text=method_totals["Amount"].apply(lambda x: f"{x:,.0f}"),
        textposition="outside",
        textfont=dict(size=11, color=TEXT_COLOR),
    ))
    fig_method.update_layout(
        **base_layout(
            height=280,
            showlegend=False,
            xaxis_tickformat=",",
            xaxis_title=None,
            yaxis_title=None,
        )
    )
    st.plotly_chart(fig_method, use_container_width=True)

# ─── Row 3: Heatmap + Top 10 Transactions ────────────────────────────────────
# FIX 3: col6 was completely empty — now filled with Top 10 Transactions table
col5, col6 = st.columns([3, 2])

with col5:
    st.markdown('<div class="section-title">Spending Heatmap — Day of Week x Month</div>', unsafe_allow_html=True)

    heatmap_data = (
        filtered.groupby(["DayOfWeek", "Month"])["Amount"]
        .sum().reset_index()
    )
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_pivot = (
        heatmap_data
        .pivot(index="DayOfWeek", columns="Month", values="Amount")
        .fillna(0)
    )
    heatmap_pivot = heatmap_pivot.reindex([d for d in day_order if d in heatmap_pivot.index])

    fig_heat = go.Figure(go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns.tolist(),
        y=heatmap_pivot.index.tolist(),
        colorscale=[[0, "#13161e"], [0.5, "#1e3a7a"], [1, "#3d7aff"]],
        hovertemplate="<b>%{y}</b> · %{x}<br>%{z:,.0f} EGP<extra></extra>",
        showscale=True,
        colorbar=dict(
            tickfont=dict(color=TEXT_COLOR, size=10),
            bgcolor=CHART_BG,
            outlinecolor=GRID_COLOR,
        )
    ))

    # FIX 1 applied here: deepcopy via base_layout() — no shallow-copy mutation
    fig_heat.update_layout(
        **base_layout(
            height=280,
            xaxis=dict(
                tickfont=dict(size=9),
                tickangle=-45,
                gridcolor=GRID_COLOR,
                zerolinecolor=GRID_COLOR,
            ),
            yaxis=dict(
                tickfont=dict(size=10),
                gridcolor=GRID_COLOR,
                zerolinecolor=GRID_COLOR,
            ),
        )
    )
    st.plotly_chart(fig_heat, use_container_width=True)

with col6:
    st.markdown('<div class="section-title">Top 10 Transactions</div>', unsafe_allow_html=True)

    top10 = (
        filtered
        .nlargest(10, "Amount")[["Date", "Category", "Amount", "Payment_Method"]]
        .copy()
    )
    top10["Date"]   = top10["Date"].dt.strftime("%Y-%m-%d")
    top10["Amount"] = top10["Amount"].apply(lambda x: f"{x:,.0f} EGP")
    top10 = top10.rename(columns={
        "Date":           "Date",
        "Category":       "Category",
        "Amount":         "Amount",
        "Payment_Method": "Method",
    })
    top10 = top10.reset_index(drop=True)
    top10.index += 1

    st.dataframe(
        top10,
        use_container_width=True,
        height=280,
    )

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#3a3f54;font-size:0.75rem;font-family:Space Mono,monospace;">'
    'Personal Finance Dashboard · 2025 · Built with Streamlit + Plotly'
    '</div>',
    unsafe_allow_html=True
)