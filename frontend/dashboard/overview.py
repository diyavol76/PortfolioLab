import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st
from typing import Optional


def render_overview(portfolio_data: dict, benchmark_data: dict):
    st.header("Portfolio Overview")

    if not portfolio_data or not portfolio_data.get("items"):
        st.info("Add stocks to your portfolio using the sidebar to see the overview.")
        return

    items = portfolio_data.get("items", [])
    total_value = portfolio_data.get("total_value", 0)
    total_cost = portfolio_data.get("total_cost", 0)
    total_return_pct = portfolio_data.get("total_return_pct", 0)
    daily_return_pct = portfolio_data.get("daily_return_pct", 0)

    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Value", f"${total_value:,.2f}")
    with col2:
        st.metric("Total Cost", f"${total_cost:,.2f}")
    with col3:
        st.metric("Total Return", f"{total_return_pct:.2f}%", delta=f"{total_return_pct:.2f}%")
    with col4:
        st.metric("Daily Return", f"{daily_return_pct:.2f}%", delta=f"{daily_return_pct:.2f}%")

    st.divider()

    col_left, col_right = st.columns(2)

    # Allocation pie chart
    with col_left:
        st.subheader("Portfolio Allocation")
        tickers = [i["ticker"] for i in items]
        # Use current prices from values
        values = []
        for item in items:
            price = item.get("current_price", item.get("cost_basis", 0))
            values.append(item["quantity"] * price)

        if sum(values) > 0:
            fig_pie = px.pie(
                names=tickers,
                values=values,
                title="Allocation by Market Value",
                hole=0.4,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No value data available for allocation chart.")

    # Holdings table
    with col_right:
        st.subheader("Holdings")
        df_items = pd.DataFrame(items)
        if not df_items.empty:
            display_cols = [c for c in ["ticker", "quantity", "cost_basis"] if c in df_items.columns]
            st.dataframe(df_items[display_cols], use_container_width=True, hide_index=True)

    st.divider()

    # Performance vs benchmark chart
    st.subheader("Performance vs S&P 500 (SPY)")

    benchmark_prices = benchmark_data.get("prices", []) if benchmark_data else []

    if benchmark_prices:
        bench_df = pd.DataFrame(benchmark_prices)
        bench_df["Date"] = pd.to_datetime(bench_df["Date"])
        bench_df = bench_df.sort_values("Date")
        if not bench_df.empty and "Close" in bench_df.columns:
            bench_df["SPY_norm"] = (bench_df["Close"] / bench_df["Close"].iloc[0] - 1) * 100

            fig_perf = go.Figure()
            fig_perf.add_trace(go.Scatter(
                x=bench_df["Date"],
                y=bench_df["SPY_norm"],
                mode="lines",
                name="S&P 500 (SPY)",
                line=dict(color="blue"),
            ))
            fig_perf.update_layout(
                title="S&P 500 Performance (YTD normalized)",
                xaxis_title="Date",
                yaxis_title="Return (%)",
                hovermode="x unified",
            )
            st.plotly_chart(fig_perf, use_container_width=True)

            # Drawdown chart
            st.subheader("S&P 500 Drawdown")
            cum = (1 + bench_df["Close"].pct_change().dropna()).cumprod()
            rolling_max = cum.cummax()
            drawdown = ((cum - rolling_max) / rolling_max) * 100

            fig_dd = go.Figure()
            fig_dd.add_trace(go.Scatter(
                x=bench_df["Date"].iloc[1:],
                y=drawdown.values,
                mode="lines",
                fill="tozeroy",
                name="Drawdown",
                line=dict(color="red"),
            ))
            fig_dd.update_layout(
                title="Drawdown (%)",
                xaxis_title="Date",
                yaxis_title="Drawdown (%)",
            )
            st.plotly_chart(fig_dd, use_container_width=True)
    else:
        st.info("Benchmark data not available.")
