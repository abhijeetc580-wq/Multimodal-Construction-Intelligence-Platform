"""
Site Safety & PPE Compliance Module.
Performs real-time multimodal worker detection, PPE verification (Hardhats, Hi-Vis Vests, Boots),
exclusion/hazard zone intrusion alerts, and OSHA compliance reporting.
"""

from pathlib import Path
from PIL import Image
import streamlit as st
import pandas as pd
from utils.cv_utils import draw_safety_annotations, pil_to_cv2
from utils.gemini_client import analyze_site_safety_vlm
from config import SAMPLE_IMAGES_DIR, SITE_ZONES

def render_safety_tab(api_key: str, model_name: str, confidence_thresh: float):
    st.markdown("### 🛡️ Real-Time Site Safety & PPE Guard")
    st.caption("Automated Computer Vision and Gemini Multimodal VLM surveillance for OSHA compliance, PPE verification, and exclusion-zone protection.")

    col_left, col_right = st.columns([1, 2], gap="medium")

    with col_left:
        st.subheader("1. Source Media")
        source_mode = st.radio(
            "Select Video/Image Stream:",
            ["Demo: Live Tower Crane Feed (CAM-04)", "Upload Site Camera Photo / Frame"],
            index=0
        )

        input_image = None
        sample_path = SAMPLE_IMAGES_DIR / "sample_site_safety.jpg"

        if source_mode == "Demo: Live Tower Crane Feed (CAM-04)":
            if sample_path.exists():
                input_image = Image.open(sample_path)
            else:
                from modules.mock_data import generate_sample_safety_frame
                input_image = generate_sample_safety_frame(sample_path)
            st.info("📹 Active Feed: `CAM-04 [East Tower Hoist & Bay 2]` (CCTV 1080p)")
        else:
            uploaded_file = st.file_uploader(
                "Upload Site Photo (JPG, PNG)",
                type=["jpg", "jpeg", "png"]
            )
            if uploaded_file is not None:
                input_image = Image.open(uploaded_file)
            elif sample_path.exists():
                input_image = Image.open(sample_path)

        st.subheader("2. Zone & Perimeter Controls")
        zone_selection = st.selectbox(
            "Active Hazard Exclusion Zone:",
            list(SITE_ZONES.keys()),
            format_func=lambda k: SITE_ZONES[k]["name"]
        )
        selected_zone_info = SITE_ZONES[zone_selection]
        st.markdown(
            f"**Risk Level:** `{selected_zone_info['risk_level']}`  \n"
            f"*{selected_zone_info['description']}*"
        )

        enable_vlm = st.checkbox(
            "Enable Gemini VLM Deep Reasoning",
            value=bool(api_key),
            help="When enabled, runs Gemini 2.5/1.5 multimodal analysis for semantic hazard detection and OSHA code citations."
        )

        run_scan = st.button("🚀 Run Site Safety Scan", type="primary", use_container_width=True)

    with col_right:
        if input_image is None:
            st.warning("Please upload an image or choose a demo stream to inspect.")
            return

        # Prepare danger zone definition for visual bounding
        danger_zone_def = {
            "name": selected_zone_info["name"],
            "box": [0.42, 0.43, 0.94, 0.79], # Normalized coordinates matching sample image
            "color": (239, 68, 68, 45)
        }

        # Detections state or run
        if run_scan or "safety_results" not in st.session_state:
            with st.spinner("Analyzing site safety vectors & PPE compliance..."):
                if enable_vlm and api_key:
                    vlm_res = analyze_site_safety_vlm(input_image, model_name=model_name, api_key=api_key)
                else:
                    vlm_res = analyze_site_safety_vlm(input_image, model_name=model_name, api_key="")

                annotated_img, summary = draw_safety_annotations(
                    input_image,
                    vlm_res.get("detections", []),
                    danger_zone=danger_zone_def
                )

                st.session_state["safety_results"] = {
                    "annotated_img": annotated_img,
                    "summary": summary,
                    "vlm_res": vlm_res
                }

        results = st.session_state.get("safety_results", {})
        annotated_img = results.get("annotated_img", input_image)
        summary = results.get("summary", {})
        vlm_res = results.get("vlm_res", {})

        # KPI Metrics Row
        score = summary.get("safety_score", 100.0)
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Safety Index", f"{score}%", delta=f"{score - 100:.1f}%" if score < 100 else "Compliant")
        col_m2.metric("Workers Onsite", summary.get("total_workers", 0))
        col_m3.metric("Compliant", summary.get("compliant_workers", 0))
        col_m4.metric("Violations Flagged", summary.get("violation_count", 0), delta_color="inverse")

        # Visual Display Tabs
        tab_anno, tab_orig = st.tabs(["🎯 Annotated AI Inspection Feed", "📷 Raw Camera Stream"])
        with tab_anno:
            st.image(annotated_img, caption="AI Safety Overlay: Green=Compliant, Red=OSHA Violation", use_container_width=True)
        with tab_orig:
            st.image(input_image, caption="Raw Input Camera Frame", use_container_width=True)

        # OSHA Violations & Recommendations
        violations = summary.get("violations", [])
        if violations:
            st.error(f"⚠️ **ACTIVE SAFETY HAZARDS DETECTED ({len(violations)} Violations)**")
            v_df = []
            for v in violations:
                v_df.append({
                    "Worker ID": v.get("worker_id"),
                    "Severity": v.get("severity"),
                    "Violations Identified": ", ".join(v.get("issues", [])),
                    "Grid Coordinates": v.get("location")
                })
            st.dataframe(pd.DataFrame(v_df), use_container_width=True)
        else:
            st.success("✅ **100% PPE COMPLIANT:** All detected personnel satisfy site head, torso, and boundary safety mandates.")

        # Executive VLM Safety Evaluation
        osha_notes = vlm_res.get("osha_summary", "")
        if osha_notes:
            with st.expander("📋 Executive OSHA Compliance & Safety Officer Evaluation", expanded=True):
                st.markdown(f"**Engine:** `{vlm_res.get('source', 'ConstructIQ AI Engine')}`")
                st.write(osha_notes)
