import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from typing import Optional


def render_metrics(ticker: str, metrics_data: dict):
    st.header(f"Financial Metrics: {ticker}")

    if not metrics_data or metrics_data.get("error"):
        st.error(f"Could not load metrics for {ticker}.")
        return

    pe = metrics_data.get("pe_ratio")
    ev_ebitda = metrics_data.get("ev_ebitda")
    peg = metrics_data.get("peg_ratio")
    roe = metrics_data.get("roe")
    ebitda_margin = metrics_data.get("ebitda_margin")
    net_margin = metrics_data.get("net_income_margin")
    rev_yoy = metrics_data.get("revenue_growth_yoy")
    rev_3y = metrics_data.get("revenue_growth_3y")
    fcf_trend = metrics_data.get("free_cash_flow_trend", [])

    # Valuation cards
    st.subheader("Valuation Multiples")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("P/E Ratio", f"{pe:.1f}x" if pe is not None else "N/A")
    with col2:
        st.metric("EV/EBITDA", f"{ev_ebitda:.1f}x" if ev_ebitda is not None else "N/A")
    with col3:
        st.metric("PEG Ratio", f"{peg:.2f}" if peg is not None else "N/A")
    with col4:
        st.metric("ROE", f"{roe:.1f}%" if roe is not None else "N/A")

    st.divider()

    col_left, col_right = st.columns(2)

    # Revenue growth bar chart
    with col_left:
        st.subheader("Revenue Growth")
        growth_labels = []
        growth_values = []
        if rev_yoy is not None:
            growth_labels.append("YoY Growth")
            growth_values.append(rev_yoy)
        if rev_3y is not None:
            growth_labels.append("3-Year CAGR")
            growth_values.append(rev_3y)

        if growth_labels:
            colors = ["green" if v >= 0 else "red" for v in growth_values]
            fig_growth = go.Figure(go.Bar(
                x=growth_labels,
                y=growth_values,
                marker_color=colors,
                text=[f"{v:.1f}%" for v in growth_values],
                textposition="outside",
            ))
            fig_growth.update_layout(
                title="Revenue Growth (%)",
                yaxis_title="Growth (%)",
                showlegend=False,
            )
            st.plotly_chart(fig_growth, use_container_width=True)
        else:
            st.info("Revenue growth data not available.")

    # Margin metrics
    with col_right:
        st.subheader("Profitability Margins")
        margin_labels = []
        margin_values = []
        if ebitda_margin is not None:
            margin_labels.append("EBITDA Margin")
            margin_values.append(ebitda_margin)
        if net_margin is not None:
            margin_labels.append("Net Income Margin")
            margin_values.append(net_margin)

        if margin_labels:
            fig_margins = go.Figure(go.Bar(
                x=margin_labels,
                y=margin_values,
                marker_color=["#2196F3", "#4CAF50"],
                text=[f"{v:.1f}%" for v in margin_values],
                textposition="outside",
            ))
            fig_margins.update_layout(
                title="Margin Analysis (%)",
                yaxis_title="Margin (%)",
                showlegend=False,
            )
            st.plotly_chart(fig_margins, use_container_width=True)
        else:
            st.info("Margin data not available.")

    # Free Cash Flow trend
    st.subheader("Free Cash Flow Trend")
    if fcf_trend:
        years = [item[0] for item in fcf_trend]
        fcf_vals = [item[1] / 1e9 for item in fcf_trend]  # Convert to billions
        colors = ["green" if v >= 0 else "red" for v in fcf_vals]

        fig_fcf = go.Figure(go.Bar(
            x=years,
            y=fcf_vals,
            marker_color=colors,
            text=[f"${v:.2f}B" for v in fcf_vals],
            textposition="outside",
        ))
        fig_fcf.update_layout(
            title="Free Cash Flow (Billions USD)",
            xaxis_title="Year",
            yaxis_title="FCF ($B)",
            showlegend=False,
        )
        st.plotly_chart(fig_fcf, use_container_width=True)
    else:
        st.info("Free cash flow data not available.")
