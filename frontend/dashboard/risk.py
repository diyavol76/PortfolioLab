import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st
from typing import Optional


def render_risk(risk_data: dict, price_data: dict):
    st.header("Risk Analysis")

    if not risk_data:
        st.info("Add stocks to your portfolio to see risk metrics.")
        return

    volatility = risk_data.get("volatility", 0)
    sharpe = risk_data.get("sharpe_ratio", 0)
    max_dd = risk_data.get("max_drawdown", 0)
    corr_matrix = risk_data.get("correlation_matrix", {})

    # Risk metric cards
    st.subheader("Risk Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Annualized Volatility",
            f"{volatility:.2f}%",
            help="Annualized standard deviation of portfolio returns",
        )
    with col2:
        st.metric(
            "Sharpe Ratio",
            f"{sharpe:.2f}",
            help="Risk-adjusted return (risk-free rate: 5%)",
        )
    with col3:
        st.metric(
            "Max Drawdown",
            f"{max_dd:.2f}%",
            help="Maximum peak-to-trough decline",
        )

    st.divider()

    # Correlation matrix heatmap
    if corr_matrix:
        st.subheader("Correlation Matrix")
        corr_df = pd.DataFrame(corr_matrix)
        if not corr_df.empty:
            fig_corr = px.imshow(
                corr_df,
                text_auto=".2f",
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1,
                title="Asset Return Correlations",
            )
            fig_corr.update_layout(height=400)
            st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Add multiple stocks to your portfolio to see correlation analysis.")

    # Rolling volatility chart
    st.subheader("Rolling Volatility (30-Day)")
    prices_list = price_data.get("prices", []) if price_data else []

    if prices_list:
        df = pd.DataFrame(prices_list)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        if "Close" in df.columns and len(df) > 30:
            returns = df["Close"].pct_change().dropna()
            rolling_vol = returns.rolling(window=30).std() * np.sqrt(252) * 100
            dates = df["Date"].iloc[1:]

            fig_vol = go.Figure()
            fig_vol.add_trace(go.Scatter(
                x=dates,
                y=rolling_vol.values,
                mode="lines",
                name="30-Day Rolling Vol",
                line=dict(color="orange"),
                fill="tozeroy",
                fillcolor="rgba(255,165,0,0.1)",
            ))
            fig_vol.update_layout(
                title="30-Day Rolling Annualized Volatility (%)",
                xaxis_title="Date",
                yaxis_title="Volatility (%)",
                hovermode="x unified",
            )
            st.plotly_chart(fig_vol, use_container_width=True)
        else:
            st.info("Not enough price data for rolling volatility chart.")
    else:
        st.info("Select a ticker in the sidebar to view volatility chart.")
