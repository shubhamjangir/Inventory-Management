import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Inventory Cost Optimization Dashboard",
    page_icon="📦",
    layout="wide",
)

# -----------------------------
# Data
# -----------------------------

def load_data() -> pd.DataFrame:
    data = [
        # 2022
        {"Year": 2022, "SKU": "A101", "Category": "Electrical", "StockQty": 420, "MonthlyUsage": 95,  "UnitCost": 20,  "ABC": "A", "Location": "WH1"},
        {"Year": 2022, "SKU": "A102", "Category": "Mechanical", "StockQty": 45,  "MonthlyUsage": 11,  "UnitCost": 200, "ABC": "A", "Location": "WH1"},
        {"Year": 2022, "SKU": "A103", "Category": "Electrical", "StockQty": 900, "MonthlyUsage": 380, "UnitCost": 5,   "ABC": "C", "Location": "WH2"},
        {"Year": 2022, "SKU": "A104", "Category": "Tools",      "StockQty": 18,  "MonthlyUsage": 3,   "UnitCost": 500, "ABC": "A", "Location": "WH1"},
        # 2023
        {"Year": 2023, "SKU": "A101", "Category": "Electrical", "StockQty": 460, "MonthlyUsage": 100, "UnitCost": 20,  "ABC": "A", "Location": "WH1"},
        {"Year": 2023, "SKU": "A102", "Category": "Mechanical", "StockQty": 48,  "MonthlyUsage": 10,  "UnitCost": 200, "ABC": "A", "Location": "WH1"},
        {"Year": 2023, "SKU": "A103", "Category": "Electrical", "StockQty": 960, "MonthlyUsage": 390, "UnitCost": 5,   "ABC": "C", "Location": "WH2"},
        {"Year": 2023, "SKU": "A104", "Category": "Tools",      "StockQty": 19,  "MonthlyUsage": 2.5, "UnitCost": 500, "ABC": "A", "Location": "WH1"},
        # 2024
        {"Year": 2024, "SKU": "A101", "Category": "Electrical", "StockQty": 500, "MonthlyUsage": 100, "UnitCost": 20,  "ABC": "A", "Location": "WH1"},
        {"Year": 2024, "SKU": "A102", "Category": "Mechanical", "StockQty": 50,  "MonthlyUsage": 10,  "UnitCost": 200, "ABC": "A", "Location": "WH1"},
        {"Year": 2024, "SKU": "A103", "Category": "Electrical", "StockQty": 1000,"MonthlyUsage": 400, "UnitCost": 5,   "ABC": "C", "Location": "WH2"},
        {"Year": 2024, "SKU": "A104", "Category": "Tools",      "StockQty": 20,  "MonthlyUsage": 2,   "UnitCost": 500, "ABC": "A", "Location": "WH1"},
        # 2025
        {"Year": 2025, "SKU": "A101", "Category": "Electrical", "StockQty": 520, "MonthlyUsage": 105, "UnitCost": 20,  "ABC": "A", "Location": "WH1"},
        {"Year": 2025, "SKU": "A102", "Category": "Mechanical", "StockQty": 52,  "MonthlyUsage": 9,   "UnitCost": 200, "ABC": "A", "Location": "WH1"},
        {"Year": 2025, "SKU": "A103", "Category": "Electrical", "StockQty": 980, "MonthlyUsage": 410, "UnitCost": 5,   "ABC": "C", "Location": "WH2"},
        {"Year": 2025, "SKU": "A104", "Category": "Tools",      "StockQty": 22,  "MonthlyUsage": 2,   "UnitCost": 500, "ABC": "A", "Location": "WH1"},
    ]
    df = pd.DataFrame(data)
    df["StockValue"] = df["StockQty"] * df["UnitCost"]
    df["StockCover"] = (df["StockQty"] / df["MonthlyUsage"]).round(2)
    df["ExcessFlag"] = df["StockCover"] > 6
    df["SlowMovingFlag"] = df["StockCover"] > 8
    df["Action"] = df.apply(
        lambda row: "Reduce" if row["StockCover"] > 8 else (
            "Control" if row["ABC"] == "A" and row["StockCover"] >= 5 else "Monitor"
        ),
        axis=1,
    )
    return df


def load_budget() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Year": [2022, 2023, 2024, 2025],
            "PlannedStockValue": [23000, 24000, 25000, 25500],
            "PlannedProcurement": [18000, 19000, 20000, 20500],
        }
    )


def format_num(x: float) -> str:
    return f"{x:,.0f}"


# -----------------------------
# Load + merge
# -----------------------------

df = load_data()
budget_df = load_budget()
years = sorted(df["Year"].unique())

# -----------------------------
# Sidebar filters
# -----------------------------

st.sidebar.title("Filters")
selected_year = st.sidebar.selectbox("Year", years, index=2)
selected_categories = st.sidebar.multiselect(
    "Category", sorted(df["Category"].unique()), default=sorted(df["Category"].unique())
)
selected_abc = st.sidebar.multiselect(
    "ABC Class", sorted(df["ABC"].unique()), default=sorted(df["ABC"].unique())
)
selected_locations = st.sidebar.multiselect(
    "Location", sorted(df["Location"].unique()), default=sorted(df["Location"].unique())
)

filtered = df[
    (df["Year"] == selected_year)
    & (df["Category"].isin(selected_categories))
    & (df["ABC"].isin(selected_abc))
    & (df["Location"].isin(selected_locations))
].copy()

planned_value = float(budget_df.loc[budget_df["Year"] == selected_year, "PlannedStockValue"].iloc[0])
planned_procurement = float(budget_df.loc[budget_df["Year"] == selected_year, "PlannedProcurement"].iloc[0])
actual_value = float(filtered["StockValue"].sum())
variance = actual_value - planned_value
excess_value = float(filtered.loc[filtered["ExcessFlag"], "StockValue"].sum())
slow_value = float(filtered.loc[filtered["SlowMovingFlag"], "StockValue"].sum())
a_class_count = int((filtered["ABC"] == "A").sum())

# -----------------------------
# Header
# -----------------------------

st.title("📦 Inventory Cost Optimization and Budget Accuracy Dashboard")
st.caption(
    "Interview-ready dashboard that connects the business problem, data analysis, ABC prioritization, optimization logic, reporting views, and final business impact."
)

# -----------------------------
# KPI Cards
# -----------------------------

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Stock Value", format_num(actual_value))
c2.metric("Planned Value", format_num(planned_value))
c3.metric("Budget Variance", format_num(variance))
c4.metric("Excess Stock Value", format_num(excess_value))
c5.metric("Slow-Moving Value", format_num(slow_value))

# -----------------------------
# Tabs
# -----------------------------

overview_tab, analysis_tab, optimization_tab, insights_tab = st.tabs(
    ["Business Overview", "Data Analysis", "Optimization Logic", "Final Insights"]
)

with overview_tab:
    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("Project Story")
        st.markdown(
            f"""
**Business Understanding**  
Inventory reports existed, but stock, consumption, and budget were not reviewed together. This caused overstock, weak control on high-value items, and budget mismatch.

**Problem Statement**  
The objective was to identify excess stock, prioritize high-value items, and improve inventory planning accuracy by combining inventory, consumption, procurement, and budget data.

**Business Importance**  
Inventory directly affects both operations and finance. In {selected_year}, actual stock value is **{format_num(actual_value)}** against planned value of **{format_num(planned_value)}**, showing why cost visibility matters.

**Requirement Focus**  
Business users needed answers to questions such as which SKUs drive value, which items are excess, and where stock is above planning assumptions.
            """
        )

    with right:
        st.subheader("Budget vs Actual")
        budget_chart = pd.DataFrame(
            {
                "Type": ["Planned Stock Value", "Actual Stock Value"],
                "Value": [planned_value, actual_value],
            }
        )
        fig_budget = px.bar(budget_chart, x="Type", y="Value", text="Value")
        fig_budget.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_budget.update_layout(height=360)
        st.plotly_chart(fig_budget, use_container_width=True)

    st.subheader("Stakeholder View")
    stakeholder_df = pd.DataFrame(
        {
            "Stakeholder": ["Planning", "Procurement", "Finance", "Management"],
            "Needs": [
                "Stock cover, excess items, action flags",
                "Current stock before ordering, high-value control",
                "Inventory value, budget variance, cost visibility",
                "Summary view of risk items and cost drivers",
            ],
        }
    )
    st.dataframe(stakeholder_df, use_container_width=True, hide_index=True)

with analysis_tab:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Stock Value by SKU")
        fig_value = px.bar(
            filtered.sort_values("StockValue", ascending=False),
            x="SKU",
            y="StockValue",
            color="ABC",
            text="StockValue",
            hover_data=["Category", "StockQty", "MonthlyUsage", "StockCover"],
        )
        fig_value.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_value.update_layout(height=420)
        st.plotly_chart(fig_value, use_container_width=True)

    with col2:
        st.subheader("Stock Cover by SKU")
        fig_cover = px.bar(
            filtered.sort_values("StockCover", ascending=False),
            x="SKU",
            y="StockCover",
            color="Action",
            text="StockCover",
            hover_data=["Category", "StockQty", "MonthlyUsage", "StockValue"],
        )
        fig_cover.update_traces(texttemplate="%{text}", textposition="outside")
        fig_cover.update_layout(height=420)
        st.plotly_chart(fig_cover, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("ABC Class Distribution")
        abc_summary = filtered.groupby("ABC", as_index=False).agg(SKUs=("SKU", "count"), Value=("StockValue", "sum"))
        fig_abc = px.pie(abc_summary, names="ABC", values="Value", hole=0.5)
        fig_abc.update_layout(height=380)
        st.plotly_chart(fig_abc, use_container_width=True)

    with col4:
        st.subheader("Category Contribution")
        category_summary = filtered.groupby("Category", as_index=False)["StockValue"].sum()
        fig_cat = px.bar(category_summary, x="Category", y="StockValue", text="StockValue")
        fig_cat.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_cat.update_layout(height=380)
        st.plotly_chart(fig_cat, use_container_width=True)

    st.subheader("Detailed SKU Analysis")
    display_df = filtered[[
        "SKU", "Category", "Location", "StockQty", "MonthlyUsage", "UnitCost", "StockValue", "StockCover", "ABC", "Action"
    ]].sort_values(["ABC", "StockValue"], ascending=[True, False])
    st.dataframe(display_df, use_container_width=True, hide_index=True)

with optimization_tab:
    st.subheader("Optimization Rules Used")
    st.markdown(
        """
- **A-class + high stock cover** → review first  
- **Low movement + high value** → reduce or rationalize  
- **Critical / high-value items** → tighter monitoring  
- **Lower value items** → simpler control  
        """
    )

    st.subheader("Priority Action Table")
    action_df = filtered[["SKU", "Category", "StockValue", "StockCover", "ABC", "Action"]].copy()
    action_df = action_df.sort_values(["Action", "StockCover", "StockValue"], ascending=[True, False, False])
    st.dataframe(action_df, use_container_width=True, hide_index=True)

    st.subheader("Exception Review")
    exception_items = filtered[(filtered["ExcessFlag"]) | (filtered["SlowMovingFlag"])].copy()
    if exception_items.empty:
        st.info("No exception items under current filters.")
    else:
        st.dataframe(
            exception_items[["SKU", "Category", "StockQty", "MonthlyUsage", "StockValue", "StockCover", "ABC", "Action"]],
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Recommended Actions")
    highest_cover_row = filtered.sort_values("StockCover", ascending=False).iloc[0] if not filtered.empty else None
    high_value_rows = filtered.sort_values("StockValue", ascending=False).head(3)
    action_text = [
        f"Review {highest_cover_row['SKU']} first for stock rationalization and procurement adjustment." if highest_cover_row is not None else "Review the highest-cover SKU first.",
        "Monitor high-value A-class items through monthly review.",
        "Use stock cover and ABC classification together in planning discussions.",
        "Align procurement review with actual usage trends and budget assumptions.",
    ]
    for item in action_text:
        st.markdown(f"- {item}")

with insights_tab:
    st.subheader("Final Insights")

    total_value_all = filtered["StockValue"].sum()
    top_value = filtered.sort_values("StockValue", ascending=False).head(3)["StockValue"].sum()
    top_share = (top_value / total_value_all * 100) if total_value_all else 0
    top_cover_sku = filtered.sort_values("StockCover", ascending=False).iloc[0]["SKU"] if not filtered.empty else "N/A"

    insight_cards = st.columns(2)
    with insight_cards[0]:
        st.info(
            f"A small number of SKUs account for most of the inventory value. Under current filters, the top items contribute **{top_share:.1f}%** of stock value."
        )
        st.info(
            f"{top_cover_sku} is the clearest excess-stock signal because it has the highest stock cover under the selected year and filters."
        )
    with insight_cards[1]:
        st.info(
            f"Actual stock value is **{format_num(actual_value)}**, which is **{format_num(variance)}** against plan, showing a planning mismatch."
        )
        st.info(
            "Targeted control on A-class and high-cover items is more effective than treating all SKUs equally."
        )

    st.subheader("Business Impact Summary")
    st.markdown(
        f"""
The dashboard shows that inventory inefficiency is concentrated in a small number of SKUs rather than being spread evenly across all items. By combining **stock value**, **stock cover**, **ABC classification**, and **budget variance** in one decision-support view, the project improves visibility for planning, procurement, finance, and management teams.

For **{selected_year}**, the dashboard highlights:
- Total stock value of **{format_num(actual_value)}** against planned value of **{format_num(planned_value)}**
- Excess stock value of **{format_num(excess_value)}**
- Slow-moving stock value of **{format_num(slow_value)}**
- **{a_class_count}** A-class items requiring the highest attention
        """
    )

# -----------------------------
# Footer
# -----------------------------

st.markdown("---")
st.caption("Built for interview presentation: connects Business Understanding, Problem Statement, Business Importance, Requirement Gathering, Stakeholders, Data Understanding, Data Analysis, ABC Analysis, Optimization Logic, Visualization, and Final Insights in one app.")
