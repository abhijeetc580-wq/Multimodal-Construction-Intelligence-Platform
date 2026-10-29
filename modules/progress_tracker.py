"""
Drone Progress Tracking & Structural Defect Inspection Module.
Provides timeline comparison between scheduled BIM/blueprints vs. actual site drone captures,
and automated OpenCV/VLM concrete crack & surface defect detection.
"""

from pathlib import Path
from PIL import Image
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.cv_utils import analyze_structural_crack, compute_visual_diff
from config import SAMPLE_IMAGES_DIR, PROJECT_MILESTONES

def render_progress_tab(api_key: str, model_name: str):
    st.markdown("### 🏗️ Drone Progress Tracking & Defect Inspector")
    st.caption("Compare site drone survey captures against scheduled BIM models and inspect concrete/masonry structures for cracks and surface defects.")

    sub_tab1, sub_tab2 = st.tabs(["🛰️ Drone Site Progress vs. Baseline BIM", "🔬 Concrete Crack & Structural Defect Inspector"])

    with sub_tab1:
        st.subheader("BIM Milestone Baseline vs. Actual Drone Survey")
        col_ctrl, col_view = st.columns([1, 2], gap="medium")

        with col_ctrl:
            st.markdown("#### Inspection Flight Settings")
            flight_date = st.date_input("Flight Survey Date:", value=pd.to_datetime("2026-10-25"))
            current_phase = st.selectbox(
                "Current Construction Phase:",
                [m["phase"] for m in PROJECT_MILESTONES],
                index=3 # Superstructure Steel Framing
            )

            diff_mode = st.radio(
                "Visualization Mode:",
                ["Side-by-Side Comparison", "AI Visual Difference Delta", "Actual Drone Survey Only"],
                index=1
            )

            st.markdown("---")
            st.markdown("#### Earned Value Summary")
            st.metric("Planned Progress", "75.0%")
            st.metric("Actual Earned Value", "68.0%", delta="-7.0% Delay", delta_color="inverse")
            st.warning("⚠️ **Variance Cause:** Exterior glazing deliveries delayed 5 days due to logistics bottleneck.")

        with col_view:
            path_plan = SAMPLE_IMAGES_DIR / "sample_drone_planned.jpg"
            path_act = SAMPLE_IMAGES_DIR / "sample_drone_actual.jpg"

            if not path_plan.exists() or not path_act.exists():
                from modules.mock_data import generate_sample_drone_progress
                img_plan, img_act = generate_sample_drone_progress(path_plan, path_act)
            else:
                img_plan = Image.open(path_plan)
                img_act = Image.open(path_act)

            if diff_mode == "Side-by-Side Comparison":
                c1, c2 = st.columns(2)
                with c1:
                    st.image(img_plan, caption="Baseline BIM Schedule Target (75%)", use_container_width=True)
                with c2:
                    st.image(img_act, caption="Actual Site Drone Capture (68%)", use_container_width=True)
            elif diff_mode == "AI Visual Difference Delta":
                diff_img = compute_visual_diff(img_plan, img_act)
                st.image(diff_img, caption="AI Delta Overlay: Highlighted zones indicate incomplete framing & uninstalled glazing", use_container_width=True)
            else:
                st.image(img_act, caption="High-Res Drone Orthomosaic Capture", use_container_width=True)

        st.markdown("---")
        st.subheader("Phase-by-Phase Milestone Progress Breakdown")
        df_milestones = pd.DataFrame(PROJECT_MILESTONES)
        
        # Plotly grouped bar chart comparing planned vs actual
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_milestones["phase"],
            y=df_milestones["planned_pct"],
            name="Planned %",
            marker_color="#94A3B8"
        ))
        fig.add_trace(go.Bar(
            x=df_milestones["phase"],
            y=df_milestones["actual_pct"],
            name="Actual Earned %",
            marker_color="#3B82F6"
        ))
        fig.update_layout(
            barmode="group",
            margin=dict(l=20, r=20, t=30, b=80),
            xaxis_tickangle=-35,
            height=340,
            yaxis=dict(title="Completion (%)", range=[0, 105])
        )
        st.plotly_chart(fig, use_container_width=True)

    with sub_tab2:
        st.subheader("Structural Concrete & Defect Analysis (ACI 224R Standard)")
        col_d1, col_d2 = st.columns([1, 2], gap="medium")

        with col_d1:
            st.markdown("#### Defect Media Source")
            defect_source = st.radio(
                "Select Surface Image:",
                ["Demo: Level 2 Shear Wall Shear Fissure", "Upload Structural Inspection Photo"],
                index=0
            )

            crack_img = None
            crack_path = SAMPLE_IMAGES_DIR / "sample_concrete_crack.jpg"

            if defect_source == "Demo: Level 2 Shear Wall Shear Fissure":
                if not crack_path.exists():
                    from modules.mock_data import generate_sample_concrete_crack
                    crack_img = generate_sample_concrete_crack(crack_path)
                else:
                    crack_img = Image.open(crack_path)
                st.info("📍 Location: `Grid Line D-4, East Core Shear Wall (Elevation +24.5ft)`")
            else:
                uploaded_crack = st.file_uploader("Upload Concrete Photo (JPG, PNG)", type=["jpg", "jpeg", "png"])
                if uploaded_crack is not None:
                    crack_img = Image.open(uploaded_crack)
                elif crack_path.exists():
                    crack_img = Image.open(crack_path)

            inspect_crack_btn = st.button("🔍 Analyze Crack Geometry & Severity", type="primary", use_container_width=True)

        with col_d2:
            if crack_img is None:
                st.warning("Please upload a concrete surface photo or use the demo image.")
                return

            annotated_crack, crack_metrics = analyze_structural_crack(crack_img)

            # Metric Cards
            m1, m2, m3 = st.columns(3)
            m1.metric("Est. Crack Length", f"{crack_metrics['estimated_max_length_mm']} mm")
            m2.metric("Est. Aperture Width", f"{crack_metrics['estimated_width_mm']} mm")
            m3.metric("Severity Rating", crack_metrics['severity'].split(' ')[0])

            # Display
            t1, t2 = st.tabs(["🔴 AI Crack Path Segmentation", "📷 Original Concrete Surface"])
            with t1:
                st.image(annotated_crack, caption="Detected crack contours traced in high-contrast red overlay", use_container_width=True)
            with t2:
                st.image(crack_img, caption="Raw Inspection Photograph", use_container_width=True)

            # Engineering assessment
            st.markdown(f"**Structural Severity:** `{crack_metrics['severity']}`")
            st.info(f"💡 **Recommended Engineering Action:**  \n{crack_metrics['action_recommendation']}")
