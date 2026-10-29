"""
Executive Health & Site Analytics Dashboard Module.
Visualizes site KPIs, safety compliance trends, project S-curves,
defect trade distribution, and geospatial risk zone heatmaps using Plotly.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from config import SITE_ZONES

def render_analytics_tab():
    st.markdown("### 📊 Executive Site Health & Analytics Dashboard")
    st.caption("Cross-discipline intelligence aggregating computer vision safety scans, milestone S-curves, and quality defect registers.")

    # Top KPI Cards Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Site Safety Index", "94.2%", delta="+2.1% this week")
    kpi2.metric("Total Active Labor", "48 Personnel", delta="8 Trades onsite")
    kpi3.metric("Schedule SPI (Earned Value)", "0.91", delta="-0.09 Delay", delta_color="inverse")
    kpi4.metric("Open Quality Defects", "10 Tickets", delta="3 Critical", delta_color="inverse")

    st.markdown("---")

    # Row 1: Charts
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.subheader("14-Day Safety Compliance Trend")
        dates = pd.date_range(end=pd.Timestamp.now(), periods=14, freq="D").strftime("%b %d")
        np.random.seed(42)
        compliance_vals = [88.5, 91.0, 89.2, 93.4, 95.0, 92.1, 94.8, 96.2, 91.5, 93.0, 95.5, 97.0, 92.8, 94.2]
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=dates,
            y=compliance_vals,
            mode="lines+markers",
            name="Daily Compliance %",
            line=dict(color="#10B981", width=3),
            marker=dict(size=7)
        ))
        fig_trend.add_hline(y=95.0, line_dash="dash", line_color="#EF4444", annotation_text="OSHA Target (95%)")
        fig_trend.update_layout(
            margin=dict(l=20, r=20, t=30, b=40),
            height=300,
            yaxis=dict(range=[80, 100], title="Compliance %")
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_c2:
        st.subheader("Project S-Curve (Planned vs Actual Earned Value)")
        weeks = [f"W{i}" for i in range(1, 25)]
        # Logistic S-curve for planned
        planned_s = [100 / (1 + np.exp(-0.35 * (i - 12))) for i in range(1, 25)]
        # Actual earned up to week 18
        actual_s = [100 / (1 + np.exp(-0.33 * (i - 12.5))) for i in range(1, 19)]
        
        fig_scurve = go.Figure()
        fig_scurve.add_trace(go.Scatter(x=weeks, y=planned_s, name="Baseline Plan", line=dict(color="#94A3B8", dash="dot", width=2)))
        fig_scurve.add_trace(go.Scatter(x=weeks[:18], y=actual_s, name="Actual Earned", line=dict(color="#3B82F6", width=3)))
        fig_scurve.update_layout(
            margin=dict(l=20, r=20, t=30, b=40),
            height=300,
            yaxis=dict(range=[0, 105], title="Cumulative Progress (%)")
        )
        st.plotly_chart(fig_scurve, use_container_width=True)

    # Row 2: Defect distribution & Zone Risk Heatmap
    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.subheader("Quality Defects by Subcontractor Trade")
        defect_data = {
            "Trade": ["Structural Concrete", "Steel Framing", "MEP / Plumbing", "Exterior Glazing", "Drywall / Finishes"],
            "Critical": [1, 0, 1, 1, 0],
            "Minor": [2, 1, 2, 1, 1]
        }
        df_defects = pd.DataFrame(defect_data)
        fig_def = px.bar(
            df_defects,
            x="Trade",
            y=["Critical", "Minor"],
            color_discrete_map={"Critical": "#EF4444", "Minor": "#F59E0B"},
            barmode="stack"
        )
        fig_def.update_layout(margin=dict(l=20, r=20, t=20, b=50), height=300)
        st.plotly_chart(fig_def, use_container_width=True)

    with col_r2:
        st.subheader("Site Zone Risk Matrix")
        zone_records = []
        for zid, zdata in SITE_ZONES.items():
            zone_records.append({
                "Zone ID": zid,
                "Zone Name": zdata["name"],
                "Risk Rating": zdata["risk_level"],
                "Workers Present": np.random.randint(4, 18),
                "Active Violations": 1 if zid == "Zone A" else 0
            })
        df_zones = pd.DataFrame(zone_records)
        st.dataframe(df_zones, use_container_width=True)

    st.markdown("---")
    st.subheader("Recent Safety & Quality Incident Ledger")
    incidents = [
        {"Ticket": "INC-104", "Timestamp": "Today 14:15", "Zone": "Zone A (Crane)", "Type": "PPE Violation", "Details": "Worker entered crane radius without hardhat", "Status": "RESOLVED (Verbal warning issued)"},
        {"Ticket": "INC-103", "Timestamp": "Today 10:45", "Zone": "Zone C (Framing)", "Type": "Fall Hazard", "Details": "Missing perimeter safety cabling at Grid F-2", "Status": "IN PROGRESS (Safety crew deployed)"},
        {"Ticket": "INC-102", "Timestamp": "Yesterday 16:30", "Zone": "Zone B (Excavation)", "Type": "Water Pooling", "Details": "Rain runoff accumulating near retaining trench", "Status": "CLOSED (Pump installed)"},
        {"Ticket": "INC-101", "Timestamp": "Yesterday 09:12", "Zone": "Zone D (Staging)", "Type": "Forklift Speed", "Details": "Delivery vehicle exceeded 10mph site limit", "Status": "RESOLVED (Subcontractor notified)"}
    ]
    st.dataframe(pd.DataFrame(incidents), use_container_width=True)
