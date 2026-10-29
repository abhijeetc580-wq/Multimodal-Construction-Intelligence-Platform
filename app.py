"""
Multimodal Construction Intelligence Platform
=============================================
A comprehensive AI-powered construction intelligence and civil engineering platform.
Built for the Skill Wallet Capstone Project.

Features:
1. Site Safety & PPE Audit (OSHA 1926 Aligned)
2. Structural Crack Diagnostics (ACI 224R Preliminary Assessment)
3. Construction Planning & Real-Estate Valuation (Indian Economics & IS 456)
4. Daily Site Assistant & Weather Advisory (Multi-turn Chat & Safety Protocols)
"""

import os
import json
from datetime import datetime
from pathlib import Path
from io import BytesIO
from typing import Dict, Any, Tuple, Optional

import streamlit as st
from PIL import Image, ImageDraw
import pandas as pd

# Optional Plotly for rich visualizations
try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# Try importing Google Generative AI
try:
    import google.generativeai as genai
    HAS_GEMINI_SDK = True
except ImportError:
    HAS_GEMINI_SDK = False

# -----------------------------------------------------------------------------
# APPLICATION CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ConstructIQ | Multimodal Construction Intelligence",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Construction-Tech CSS Theme
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header Banner */
.construction-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    border-left: 6px solid #FF6B00;
    padding: 1.4rem 1.8rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.construction-header h1 {
    color: #F8FAFC !important;
    font-size: 1.85rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.025em;
}

.construction-header p {
    color: #94A3B8 !important;
    font-size: 0.95rem;
    margin-top: 0.4rem;
    margin-bottom: 0;
}

/* Status Badges */
.badge-live {
    background-color: #065F46;
    color: #34D399;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    display: inline-block;
}

.badge-demo {
    background-color: #78350F;
    color: #FBBF24;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    display: inline-block;
}

/* Callout Disclaimers */
.disclaimer-banner {
    background-color: #FFFBEB;
    border: 1px solid #FCD34D;
    border-left: 4px solid #F59E0B;
    color: #92400E;
    padding: 0.85rem 1.1rem;
    border-radius: 6px;
    margin-bottom: 1.2rem;
    font-size: 0.88rem;
    line-height: 1.45;
}

.engineering-warning {
    background-color: #FEF2F2;
    border: 1px solid #FECACA;
    border-left: 4px solid #EF4444;
    color: #991B1B;
    padding: 0.85rem 1.1rem;
    border-radius: 6px;
    margin-bottom: 1.2rem;
    font-size: 0.88rem;
    line-height: 1.45;
}

/* Card Styling */
.stat-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Monospace metrics */
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
}

/* Primary Button Styling */
button[kind="primary"] {
    background-color: #FF6B00 !important;
    border-color: #EA580C !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

button[kind="primary"]:hover {
    background-color: #EA580C !important;
    border-color: #C2410C !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# INDIAN CURRENCY FORMATTING UTILITY
# -----------------------------------------------------------------------------
def format_inr(number: float, with_words: bool = True) -> str:
    """
    Format a numeric amount into Indian Rupee format (Lakhs and Crores).
    Example: 12500000 -> '₹ 1.25 Crore' or '₹ 1,25,00,000'
    """
    if number is None or pd.isna(number):
        return "₹ 0"
    
    amount = float(number)
    sign = "-" if amount < 0 else ""
    amount = abs(amount)

    if with_words:
        if amount >= 10000000: # 1 Crore = 10,000,000
            crores = amount / 10000000
            return f"{sign}₹ {crores:.2f} Crore"
        elif amount >= 100000: # 1 Lakh = 100,000
            lakhs = amount / 100000
            return f"{sign}₹ {lakhs:.2f} Lakh"
        else:
            return f"{sign}₹ {amount:,.0f}"
    
    # Standard Indian Comma Separation
    s = f"{amount:.0f}"
    if len(s) <= 3:
        formatted = s
    else:
        last3 = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted = ",".join(groups) + "," + last3
    return f"{sign}₹ {formatted}"

# -----------------------------------------------------------------------------
# SAMPLE ASSETS GENERATION & DISCOVERY
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = BASE_DIR / "assets" / "sample_images"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

def generate_sample_safety_image(filepath: Path) -> Image.Image:
    """Generate a clean synthetic construction worker image for testing."""
    w, h = 800, 500
    img = Image.new("RGB", (w, h), color=(140, 155, 170))
    draw = ImageDraw.Draw(img)
    # Sky & background
    draw.rectangle([0, 0, w, 180], fill=(180, 205, 230))
    # Crane in background
    draw.rectangle([460, 20, 480, 260], fill=(234, 88, 12))
    draw.line([300, 35, 650, 35], fill=(234, 88, 12), width=5)
    # Steel frame
    for x in range(60, w, 180):
        draw.rectangle([x, 80, x + 15, 360], fill=(70, 80, 95))
    # Worker 1: Compliant (Yellow hardhat, hi-vis vest, boots)
    draw.ellipse([180, 200, 215, 235], fill=(250, 204, 21)) # Yellow hardhat
    draw.rectangle([175, 240, 220, 310], fill=(74, 222, 128)) # Hi-vis green
    draw.rectangle([180, 310, 215, 380], fill=(30, 41, 59)) # Pants & boots
    # Worker 2: Violation (No hardhat, dark hair, near crane)
    draw.ellipse([475, 215, 505, 245], fill=(30, 20, 15)) # Dark hair (No Helmet!)
    draw.rectangle([470, 250, 510, 315], fill=(249, 115, 22)) # Orange vest
    draw.rectangle([475, 315, 505, 380], fill=(51, 65, 85))
    img.save(filepath, quality=95)
    return img

def generate_sample_crack_image(filepath: Path) -> Image.Image:
    """Generate a clean synthetic concrete surface with visible crack for testing."""
    w, h = 800, 500
    img = Image.new("RGB", (w, h), color=(170, 175, 180))
    draw = ImageDraw.Draw(img)
    # Concrete variations
    for i in range(20, w, 40):
        draw.line([i, 0, i, h], fill=(160, 165, 170), width=1)
    # Meandering diagonal crack (Structural Shear angle ~45 deg)
    points = [
        (150, 80), (220, 130), (280, 170), (360, 230),
        (420, 270), (510, 340), (590, 400), (660, 440)
    ]
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=(30, 30, 30), width=3)
        # Minor hairline branch
        if i == 2:
            draw.line([points[i], (points[i][0] + 35, points[i][1] + 25)], fill=(50, 50, 50), width=1)
    # Scale reference bar
    draw.rectangle([40, 440, 200, 475], fill=(255, 255, 255), outline=(0, 0, 0), width=1)
    draw.line([50, 458, 190, 458], fill=(0, 0, 0), width=2)
    draw.text((70, 444), "SCALE: 50 mm", fill=(0, 0, 0))
    img.save(filepath, quality=95)
    return img

sample_safety_path = SAMPLE_DIR / "sample_site_safety.jpg"
sample_crack_path = SAMPLE_DIR / "sample_concrete_crack.jpg"
if not sample_safety_path.exists():
    generate_sample_safety_image(sample_safety_path)
if not sample_crack_path.exists():
    generate_sample_crack_image(sample_crack_path)

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS & API CONFIGURATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🏗️ **ConstructIQ**")
    st.markdown("**Multimodal Construction Intelligence**")
    st.caption("Skill Wallet Capstone Project • AI Site Intelligence")
    st.markdown("---")

    st.subheader("⚙️ System Mode & API Key")
    env_key = os.getenv("GEMINI_API_KEY", "").strip()
    user_key = st.text_input(
        "Google Gemini API Key:",
        value=env_key,
        type="password",
        placeholder="AIzaSy...",
        help="Paste your Gemini API key to activate live multimodal AI. If left empty, the application runs in robust, fully-functional DEMO MODE."
    ).strip()

    active_key = user_key if user_key else env_key
    is_live_mode = bool(active_key and HAS_GEMINI_SDK)

    if is_live_mode:
        st.markdown('<span class="badge-live">🟢 LIVE AI MODE ACTIVE</span>', unsafe_allow_html=True)
        st.caption("Connected to Google Gemini API. Vision and multimodal reasoning enabled.")
    else:
        st.markdown('<span class="badge-demo">🟡 DEMO MODE (SIMULATED AI)</span>', unsafe_allow_html=True)
        st.caption("No valid API key detected. Results are simulated demonstration heuristics.")

    model_choice = st.selectbox(
        "Gemini Model Selection:",
        ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0,
        disabled=not is_live_mode
    )

    st.markdown("---")
    st.markdown("### 📋 Navigation")
    app_section = st.radio(
        "Select Platform Module:",
        [
            "🦺 1. Site Safety & PPE Audit",
            "🔍 2. Structural Crack Diagnostics",
            "📊 3. Construction Planning & Valuation",
            "🌦️ 4. Daily Assistant & Weather Advisory"
        ],
        index=0
    )

    st.markdown("---")
    if st.button("🔄 Reset App Session & Cache", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.caption("ConstructIQ v1.0.0 Pro • OSHA 1926, ACI 318 & IS 456 Aligned")

# -----------------------------------------------------------------------------
# MAIN APP HEADER
# -----------------------------------------------------------------------------
current_time_str = datetime.now().strftime("%A, %d %B %Y | %H:%M IST")
st.markdown(f"""
<div class="construction-header">
    <h1>🏗️ Multimodal Construction Intelligence Platform</h1>
    <p><b>Executive Project Hub</b> &bull; {current_time_str} &bull; 
    {'<span class="badge-live">LIVE AI</span>' if is_live_mode else '<span class="badge-demo">DEMO MODE</span>'}
    </p>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# FEATURE 1: SITE SAFETY & PPE AUDIT
# =============================================================================
def run_safety_audit(image: Image.Image, api_key: str, model_name: str) -> Dict[str, Any]:
    """Analyze construction-site image for PPE compliance and site safety hazards."""
    if not api_key or not HAS_GEMINI_SDK:
        # Realistic simulated audit data for DEMO MODE
        return {
            "mode": "DEMO / SIMULATED AUDIT",
            "is_demo": True,
            "timestamp": datetime.now().isoformat(),
            "safety_score": 68,
            "overall_status": "MODERATE RISK - CORRECTIVE INTERVENTION REQUIRED",
            "status_badge_color": "#F59E0B",
            "personnel_detected": 2,
            "compliant_workers": 1,
            "non_compliant_workers": 1,
            "ppe_checklist": [
                {"equipment": "Helmets / Hard Hats", "standard": "OSHA 1926.100", "status": "Partial", "compliant": False, "notes": "Worker #2 near crane radius observed without required Type I head protection."},
                {"equipment": "High-Visibility Safety Vests", "standard": "ANSI/ISEA 107", "status": "Pass", "compliant": True, "notes": "Class 2 fluorescent orange and green reflective vests verified on all personnel."},
                {"equipment": "Steel-Toe Protective Boots", "standard": "OSHA 1926.96", "status": "Pass", "compliant": True, "notes": "Industrial grade protective work boots observed on all visible workers."},
                {"equipment": "Fall Arrest Harness", "standard": "OSHA 1926.501", "status": "Not Required", "compliant": True, "notes": "Ground-level structural bay work; no personnel at heights exceeding 6 feet."}
            ],
            "detected_hazards": [
                {
                    "hazard_id": "HAZ-001",
                    "severity": "Critical",
                    "category": "Head Injury & Suspended Load Zone",
                    "description": "Worker #2 is active within the crane swing radius without a certified protective hardhat.",
                    "corrective_action": "Halt work in crane radius immediately. Issue OSHA-compliant hardhat before permitting re-entry."
                },
                {
                    "hazard_id": "HAZ-002",
                    "severity": "Medium",
                    "category": "Demarcation Slack",
                    "description": "Exclusion perimeter boundary tape is loose near the central staging corridor.",
                    "corrective_action": "Re-tension hazard perimeter demarcation cables and verify high-visibility warning flags."
                }
            ],
            "osha_summary": "Simulated Audit: 1 critical infraction identified under OSHA 1926.100 (Head Protection). 1 worker compliant with full PPE suite, 1 worker non-compliant in high-risk zone."
        }

    # LIVE AI MODE via Gemini VLM
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        prompt = """
You are a senior OSHA Jobsite Safety Inspector (OSHA 500 Certified).
Inspect this construction site image for PPE compliance and safety hazards.
Analyze visible equipment:
1. Helmets / Hard Hats (OSHA 1926.100)
2. High-visibility safety vests (ANSI/ISEA 107)
3. Protective boots (OSHA 1926.96)
4. Safety harnesses (OSHA 1926.501) if working at heights or near open ledges.

Return a strictly valid JSON object matching this exact schema:
{
  "mode": "LIVE AI AUDIT (Gemini Multimodal VLM)",
  "is_demo": false,
  "timestamp": "ISO timestamp",
  "safety_score": integer between 0 and 100,
  "overall_status": "COMPLIANT" or "MODERATE RISK" or "CRITICAL HAZARD",
  "status_badge_color": "#10B981" for compliant, "#F59E0B" for moderate, "#EF4444" for critical,
  "personnel_detected": integer,
  "compliant_workers": integer,
  "non_compliant_workers": integer,
  "ppe_checklist": [
    {
      "equipment": "name of PPE item",
      "standard": "OSHA regulation citation",
      "status": "Pass" or "Fail" or "Partial" or "Not Required",
      "compliant": boolean,
      "notes": "specific observation from image"
    }
  ],
  "detected_hazards": [
    {
      "hazard_id": "HAZ-001",
      "severity": "Low" or "Medium" or "High" or "Critical",
      "category": "hazard category",
      "description": "detailed description of hazard seen in image",
      "corrective_action": "actionable step site superintendent must take"
    }
  ],
  "osha_summary": "Executive summary with regulatory citations and safety recommendations."
}
Return ONLY pure JSON without markdown backticks or extra text.
"""
        response = model.generate_content([prompt, image])
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        # Fallback to simulated if API error occurs
        demo_res = run_safety_audit(image, "", "")
        demo_res["osha_summary"] += f" (Note: Live AI call returned '{str(e)}', reverted to simulated mode)."
        return demo_res


if app_section == "🦺 1. Site Safety & PPE Audit":
    st.subheader("🦺 Feature 1: Construction Site Safety & PPE Audit")
    st.caption("Upload jobsite photographs to automatically verify PPE compliance, calculate jobsite safety scores, and flag OSHA safety infractions.")

    if not is_live_mode:
        st.markdown("""
        <div class="disclaimer-banner">
            ⚠️ <b>DEMO MODE / SIMULATED AUDIT DISCLAIMER</b><br/>
            No Google Gemini API key is configured. Results displayed below are <b>simulated demonstration heuristics</b>. 
            No actual computer vision or deep learning inference was performed on this image. 
            To activate live visual inspection, enter your Gemini API key in the left sidebar.
        </div>
        """, unsafe_allow_html=True)

    col_upload, col_display = st.columns([1, 1.2], gap="large")

    with col_upload:
        st.markdown("#### 1. Select Construction Image")
        source_type = st.radio("Choose Input Method:", ["Upload Image File (JPG, JPEG, PNG)", "Use Pre-loaded Jobsite Sample"], horizontal=True)
        
        audit_image = None
        if source_type == "Upload Image File (JPG, JPEG, PNG)":
            uploaded_file = st.file_uploader("Upload Jobsite Photo", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                try:
                    audit_image = Image.open(uploaded_file).convert("RGB")
                except Exception as e:
                    st.error(f"Error loading image: {e}")
        else:
            if sample_safety_path.exists():
                audit_image = Image.open(sample_safety_path).convert("RGB")
                st.info("Loaded pre-configured test frame: `Tower Crane & Structural Framing Bay (CAM-04)`")

        if audit_image:
            st.image(audit_image, caption="Inspection Target Image", use_container_width=True)
            scan_btn = st.button("🚀 Run Site Safety & PPE Inspection", type="primary", use_container_width=True)
        else:
            st.warning("Please upload a construction-site image or choose the sample image above.")
            scan_btn = False

    with col_display:
        st.markdown("#### 2. Safety Audit Report & Diagnostics")
        
        if audit_image and (scan_btn or "safety_audit_cache" in st.session_state):
            if scan_btn or "safety_audit_cache" not in st.session_state:
                with st.spinner("Inspecting personnel, headgear, safety vests, and work perimeters..."):
                    audit_data = run_safety_audit(
                        image=audit_image,
                        api_key=active_key if is_live_mode else "",
                        model_name=model_choice
                    )
                    st.session_state["safety_audit_cache"] = audit_data

            res = st.session_state["safety_audit_cache"]

            # Top KPI metrics
            score = res.get("safety_score", 0)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Safety Score", f"{score}/100")
            m2.metric("Personnel", res.get("personnel_detected", 0))
            m3.metric("Compliant", res.get("compliant_workers", 0))
            m4.metric("Non-Compliant", res.get("non_compliant_workers", 0), delta_color="inverse")

            # Overall Status Alert
            status_text = res.get("overall_status", "UNKNOWN")
            if score >= 85:
                st.success(f"✅ **STATUS: {status_text}**")
            elif score >= 60:
                st.warning(f"⚠️ **STATUS: {status_text}**")
            else:
                st.error(f"🚨 **STATUS: {status_text}**")

            # PPE Checklist Table
            st.markdown("##### 📋 PPE Compliance Checklist")
            checklist = res.get("ppe_checklist", [])
            if checklist:
                df_check = pd.DataFrame(checklist)
                st.dataframe(df_check, use_container_width=True)

            # Detected Hazards with Severity
            st.markdown("##### ⚠️ Detected Hazards & Corrective Actions")
            hazards = res.get("detected_hazards", [])
            if hazards:
                for h in hazards:
                    sev = h.get("severity", "Medium")
                    sev_icon = "🔴" if sev in ["Critical", "High"] else ("🟡" if sev == "Medium" else "🟢")
                    with st.expander(f"{sev_icon} [{sev.upper()}] {h.get('category')}: {h.get('description')}", expanded=True):
                        st.markdown(f"**Identified Hazard:** {h.get('description')}")
                        st.markdown(f"**Recommended Action:** `{h.get('corrective_action')}`")
            else:
                st.info("No active hazards detected in this scene.")

            # OSHA Summary
            st.markdown("##### 📝 Executive Inspector Summary")
            st.info(res.get("osha_summary", "Inspection completed."))

            # Downloadable JSON Report
            st.markdown("##### 💾 Export Audit Data")
            json_str = json.dumps(res, indent=2)
            st.download_button(
                label="⬇️ Download Structured Audit Report (JSON)",
                data=json_str,
                file_name=f"Site_Safety_Audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
            with st.expander("👁️ View Raw JSON Output"):
                st.json(res)


# =============================================================================
# FEATURE 2: CRACK DIAGNOSTICS
# =============================================================================
def run_crack_diagnostic(image: Image.Image, api_key: str, model_name: str) -> Dict[str, Any]:
    """Classify structural crack/defect, estimate width, urgency, and recommended actions."""
    if not api_key or not HAS_GEMINI_SDK:
        # Realistic simulated defect diagnostic for DEMO MODE
        return {
            "mode": "DEMO / SIMULATED DEFECT ANALYSIS",
            "is_demo": True,
            "timestamp": datetime.now().isoformat(),
            "element_type": "Reinforced Concrete Shear Wall / Core Bay",
            "primary_defect": "Structural Shear",
            "alternative_classifications": ["Settlement", "Thermal Expansion"],
            "estimated_crack_width": "1.8 mm - 2.5 mm",
            "severity_level": "High",
            "urgency": "Urgent Engineering Review Required",
            "possible_causes": [
                "Diagonal tension shear stress exceeding concrete tensile capacity under localized load transfer",
                "Differential foundation settlement causing shear deformation along the wall plane",
                "Restrained thermal contraction combined with early-age drying shrinkage"
            ],
            "recommended_next_steps": [
                "Install calibrated mechanical crack tell-tale monitoring gauges across the fissure to track active movement over 14 days.",
                "Commission a formal physical site inspection by a licensed Structural Engineer of Record (SEOR).",
                "Perform non-destructive Ultrasonic Pulse Velocity (UPV) testing to determine crack depth and rebar debonding.",
                "If movement is dormant, prepare surface and execute low-pressure epoxy resin injection per ACI 503R."
            ],
            "technical_notes": "Diagonal orientation (~45 degrees) spanning multiple aggregate paths strongly indicates shear distress rather than benign surface shrinkage."
        }

    # LIVE AI MODE via Gemini VLM
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        prompt = """
You are a licensed Senior Forensic Structural Engineer (PE / SE) specializing in concrete pathology per ACI 224R-01.
Analyze this image of a concrete wall, slab, or masonry surface for cracks and defects.
Classify the defect into one of these standard engineering categories:
- Hairline
- Settlement
- Structural Shear
- Thermal Expansion
- Spalling

Return a strictly valid JSON object matching this exact schema:
{
  "mode": "LIVE AI DEFECT ANALYSIS (Gemini Multimodal VLM)",
  "is_demo": false,
  "timestamp": "ISO timestamp",
  "element_type": "identified building element (e.g. Concrete Beam, Shear Wall, Slab, Brick Masonry)",
  "primary_defect": "Hairline" or "Settlement" or "Structural Shear" or "Thermal Expansion" or "Spalling",
  "alternative_classifications": ["list of other possible classifications considered"],
  "estimated_crack_width": "e.g. < 0.3 mm or 1.0 - 2.0 mm or > 5.0 mm based on visual scale",
  "severity_level": "Low" or "Moderate" or "High" or "Critical",
  "urgency": "Routine Monitoring" or "Priority Inspection" or "Urgent Engineering Review Required" or "Immediate Shoring Required",
  "possible_causes": [
    "detailed engineering cause 1",
    "detailed engineering cause 2"
  ],
  "recommended_next_steps": [
    "actionable structural engineering remediation step 1",
    "actionable structural engineering remediation step 2",
    "actionable structural engineering remediation step 3"
  ],
  "technical_notes": "Engineering observations explaining orientation, pattern, and structural significance."
}
Return ONLY pure JSON without markdown backticks or commentary.
"""
        response = model.generate_content([prompt, image])
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        demo_res = run_crack_diagnostic(image, "", "")
        demo_res["technical_notes"] += f" (Note: Live AI call returned '{str(e)}', reverted to simulated mode)."
        return demo_res


if app_section == "🔍 2. Structural Crack Diagnostics":
    st.subheader("🔍 Feature 2: Structural Crack & Surface Defect Diagnostics")
    st.caption("Inspect concrete, masonry, and wall surfaces to classify crack topologies per ACI 224R standards and receive engineering recommendations.")

    # Mandatory Structural Engineering Warning
    st.markdown("""
    <div class="engineering-warning">
        ⚠️ <b>MANDATORY STRUCTURAL ENGINEERING DISCLAIMER</b><br/>
        This computer vision diagnostic tool provides <b>preliminary, non-destructive estimates only</b>. 
        It cannot and does not replace an in-person physical inspection, core sampling, or formal evaluation by a licensed Professional Engineer (PE) or qualified Structural Consultant. Never make structural alteration or load-bearing decisions based solely on preliminary photographic scans.
    </div>
    """, unsafe_allow_html=True)

    if not is_live_mode:
        st.markdown("""
        <div class="disclaimer-banner">
            ⚠️ <b>DEMO MODE / SIMULATED DEFECT DISCLAIMER</b><br/>
            Running without a Gemini API key. Defect classification, aperture measurements, and causes shown below are <b>simulated demonstration data</b>.
        </div>
        """, unsafe_allow_html=True)

    col_c1, col_c2 = st.columns([1, 1.2], gap="large")

    with col_c1:
        st.markdown("#### 1. Select Structural Surface Image")
        crack_input_mode = st.radio("Choose Input Method:", ["Upload Concrete/Wall Photo", "Use Pre-loaded Crack Sample"], horizontal=True)

        crack_image = None
        if crack_input_mode == "Upload Concrete/Wall Photo":
            uploaded_crack = st.file_uploader("Upload Image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])
            if uploaded_crack:
                try:
                    crack_image = Image.open(uploaded_crack).convert("RGB")
                except Exception as e:
                    st.error(f"Error reading image: {e}")
        else:
            if sample_crack_path.exists():
                crack_image = Image.open(sample_crack_path).convert("RGB")
                st.info("Loaded pre-configured concrete specimen: `Shear Wall Core Bay Sample`")

        if crack_image:
            st.image(crack_image, caption="Structural Concrete Surface Target", use_container_width=True)
            diag_btn = st.button("🔬 Analyze Crack Geometry & Defect Type", type="primary", use_container_width=True)
        else:
            st.warning("Please upload a concrete surface photo or choose the sample above.")
            diag_btn = False

    with col_c2:
        st.markdown("#### 2. Diagnostic Assessment & Remediation")

        if crack_image and (diag_btn or "crack_diag_cache" in st.session_state):
            if diag_btn or "crack_diag_cache" not in st.session_state:
                with st.spinner("Classifying fissure morphology, estimating crack width, and assessing urgency..."):
                    diag_data = run_crack_diagnostic(
                        image=crack_image,
                        api_key=active_key if is_live_mode else "",
                        model_name=model_choice
                    )
                    st.session_state["crack_diag_cache"] = diag_data

            cd = st.session_state["crack_diag_cache"]

            # Diagnostic Metric Cards
            k1, k2, k3 = st.columns(3)
            k1.metric("Defect Classification", cd.get("primary_defect", "Unknown"))
            k2.metric("Est. Crack Width", cd.get("estimated_crack_width", "N/A"))
            k3.metric("Urgency", cd.get("urgency", "Review Required"))

            # Classification Card
            defect_type = cd.get("primary_defect", "")
            st.markdown(f"**Structural Element:** `{cd.get('element_type', 'Concrete Surface')}`")
            st.markdown(f"**Primary Defect Category:** `{defect_type}`")
            if cd.get("alternative_classifications"):
                st.caption(f"Differential possibilities considered: {', '.join(cd['alternative_classifications'])}")

            # Possible Causes
            st.markdown("##### ❓ Probable Engineering Causes")
            causes = cd.get("possible_causes", [])
            for c in causes:
                st.markdown(f"- {c}")

            # Recommended Next Steps
            st.markdown("##### 🛠️ Recommended Structural Protocol")
            steps = cd.get("recommended_next_steps", [])
            for s in steps:
                st.markdown(f"1. {s}")

            # Engineering Notes
            if cd.get("technical_notes"):
                with st.expander("📑 Technical Forensic Notes", expanded=True):
                    st.write(cd["technical_notes"])

            # Downloadable JSON Results
            st.markdown("##### 💾 Export Diagnostic Report")
            c_json = json.dumps(cd, indent=2)
            st.download_button(
                label="⬇️ Download Diagnostic Report (JSON)",
                data=c_json,
                file_name=f"Structural_Crack_Diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
            with st.expander("👁️ View Raw JSON Data"):
                st.json(cd)


# =============================================================================
# FEATURE 3: CONSTRUCTION PLANNING & REAL-ESTATE VALUATION (INR)
# =============================================================================
if app_section == "📊 3. Construction Planning & Valuation":
    st.subheader("📊 Feature 3: Construction Budget Planning & Real-Estate Valuation (INR)")
    st.caption("Plan project financials, forecast material demands (Cement & Steel), track expenditure against completion %, and model property valuations across Indian real estate tiers.")

    # Valuation Disclaimer
    st.markdown("""
    <div class="disclaimer-banner">
        ⚠️ <b>VALUATION & PLANNING DISCLAIMER</b><br/>
        Financial figures, material quantities, and property valuations are <b>indicative models based on Indian civil engineering standards (IS 456) and regional market averages</b>. 
        They do not constitute guaranteed contractor bids, statutory tax appraisals, or bank loan guarantees. Adjust assumptions below to reflect local site conditions.
    </div>
    """, unsafe_allow_html=True)

    col_p1, col_p2 = st.columns([1, 1], gap="large")

    with col_p1:
        st.markdown("#### 1. Project Specifications")
        structure_type = st.selectbox(
            "Structure Type:",
            [
                "Residential (Apartment / High-Rise)",
                "Residential (Independent Villa / Row House)",
                "Commercial Office / Retail Complex",
                "Industrial Shed / Warehouse"
            ],
            index=0
        )

        built_up_area = st.number_input(
            "Built-Up Area (Square Feet):",
            min_value=500,
            max_value=1000000,
            value=12000,
            step=500,
            help="Total gross constructed floor area in sq. ft."
        )

        city_tier = st.selectbox(
            "Indian Location / City Tier:",
            [
                "Tier 1 (Mumbai, Delhi-NCR, Bengaluru, Hyderabad, Chennai, Pune)",
                "Tier 2 (Ahmedabad, Jaipur, Chandigarh, Kochi, Lucknow, Indore, Coimbatore)",
                "Tier 3 / Emerging Urban Centers"
            ],
            index=0
        )

        # Baseline cost benchmarks by structure & tier
        cost_defaults = {
            "Residential (Apartment / High-Rise)": 2400.0,
            "Residential (Independent Villa / Row House)": 2100.0,
            "Commercial Office / Retail Complex": 2800.0,
            "Industrial Shed / Warehouse": 1650.0
        }
        tier_multipliers = {
            "Tier 1 (Mumbai, Delhi-NCR, Bengaluru, Hyderabad, Chennai, Pune)": 1.15,
            "Tier 2 (Ahmedabad, Jaipur, Chandigarh, Kochi, Lucknow, Indore, Coimbatore)": 1.0,
            "Tier 3 / Emerging Urban Centers": 0.85
        }
        computed_default_cost = round(cost_defaults[structure_type] * tier_multipliers[city_tier], 0)

        cost_per_sqft = st.number_input(
            "Estimated Construction Cost per Sq. Ft. (₹):",
            min_value=800.0,
            max_value=12000.0,
            value=float(computed_default_cost),
            step=50.0,
            help="Adjustable based on finishing grade (Basic, Standard, Premium, Luxury)."
        )

        completion_pct = st.slider(
            "Construction Progress / Completion (%):",
            min_value=0.0,
            max_value=100.0,
            value=65.0,
            step=1.0,
            help="Current milestone percentage achieved onsite."
        )

        with st.expander("⚙️ Adjust Engineering & Material Assumptions"):
            st.markdown("**Material Coefficients (per sq. ft. of built-up area):**")
            cement_factor = st.slider("Cement Bags per sq. ft. (IS 456 benchmark: 0.40 - 0.45):", 0.30, 0.60, 0.42, 0.01)
            steel_factor_kg = st.slider("Steel (TMT Rebar) in kg per sq. ft. (IS 456 benchmark: 3.5 - 4.5):", 2.0, 7.0, 4.0, 0.1)
            st.markdown("**Unit Cost Assumptions:**")
            cement_rate_bag = st.number_input("Cement Bag Rate (₹ per 50kg bag):", min_value=250.0, max_value=600.0, value=380.0, step=10.0)
            steel_rate_kg = st.number_input("TMT Steel Rebar Rate (₹ per kg):", min_value=40.0, max_value=120.0, value=65.0, step=2.0)
            
            # Market Real Estate Selling Rate assumption
            base_market_rates = {
                "Tier 1 (Mumbai, Delhi-NCR, Bengaluru, Hyderabad, Chennai, Pune)": 8500.0,
                "Tier 2 (Ahmedabad, Jaipur, Chandigarh, Kochi, Lucknow, Indore, Coimbatore)": 5200.0,
                "Tier 3 / Emerging Urban Centers": 3400.0
            }
            market_selling_rate = st.number_input(
                "Estimated Finished Market Selling Rate (₹ per sq. ft.):",
                min_value=1500.0,
                max_value=50000.0,
                value=float(base_market_rates[city_tier]),
                step=250.0
            )

    # Computations
    total_budget = built_up_area * cost_per_sqft
    expenditure_to_date = total_budget * (completion_pct / 100.0)
    remaining_budget = total_budget - expenditure_to_date

    # Material quantities
    total_cement_bags = int(built_up_area * cement_factor)
    total_cement_cost = total_cement_bags * cement_rate_bag

    total_steel_kg = built_up_area * steel_factor_kg
    total_steel_tonnes = round(total_steel_kg / 1000.0, 2)
    total_steel_cost = total_steel_kg * steel_rate_kg

    total_sand_cft = int(built_up_area * 1.8)
    total_aggregate_cft = int(built_up_area * 1.2)

    # Real Estate Valuation
    # Fully completed property market value
    full_market_value = built_up_area * market_selling_rate
    # Indicative current valuation factors land/construction progress
    # Valuation model: 45% land & entitlement + 55% built structure progress
    indicative_current_valuation = full_market_value * (0.45 + 0.55 * (completion_pct / 100.0))

    with col_p2:
        st.markdown("#### 2. Financial & Valuation Overview")

        # Top Financial Cards
        f1, f2 = st.columns(2)
        f1.metric("Total Project Budget", format_inr(total_budget))
        f2.metric("Expenditure to Date", format_inr(expenditure_to_date), f"{completion_pct:.0f}% Completed")

        f3, f4 = st.columns(2)
        f3.metric("Remaining Budget", format_inr(remaining_budget))
        f4.metric("Indicative Current Valuation", format_inr(indicative_current_valuation))

        st.markdown(f"**Fully Completed Market Potential:** `{format_inr(full_market_value)}`")

        # Construction Progress Bar with stage milestone
        st.markdown("##### 📈 Physical Milestone Progress")
        st.progress(completion_pct / 100.0)

        # Milestone Tag
        if completion_pct < 20:
            stage_name = "Substructure, Deep Piling & Footings"
        elif completion_pct < 50:
            stage_name = "Superstructure RCC Columns & Slabs"
        elif completion_pct < 80:
            stage_name = "Masonry, MEP Rough-Ins & Glazing"
        elif completion_pct < 100:
            stage_name = "Interior Finishes, Flooring & Fixtures"
        else:
            stage_name = "Fully Commissioned / Handover Ready"
        st.caption(f"**Current Milestone Stage ({completion_pct:.0f}%):** *{stage_name}*")

        st.markdown("---")
        st.markdown("##### 🏗️ Critical Material Demand Forecast (IS 456 Specification)")

        mat_col1, mat_col2 = st.columns(2)
        with mat_col1:
            st.metric("Total Cement Required", f"{total_cement_bags:,} Bags", f"~{total_cement_bags*50/1000:.1f} Tonnes")
            st.caption(f"Estimated Cement Outlay: **{format_inr(total_cement_cost)}** (@ ₹{cement_rate_bag:.0f}/bag)")
            st.markdown(f"- Coarse Aggregate: **{total_aggregate_cft:,} cu. ft.**")
        
        with mat_col2:
            st.metric("Total Steel (TMT Rebar)", f"{total_steel_tonnes} Tonnes", f"{total_steel_kg:,.0f} kg")
            st.caption(f"Estimated Steel Outlay: **{format_inr(total_steel_cost)}** (@ ₹{steel_rate_kg:.0f}/kg)")
            st.markdown(f"- Sand / M-Sand: **{total_sand_cft:,} cu. ft.**")

        # Visual Cost Breakdown
        if HAS_PLOTLY:
            cost_dist_df = pd.DataFrame({
                "Category": ["Structural Steel", "Cement & Concrete", "Labor & Finishing", "Other MEP / Finishes"],
                "Amount_INR": [
                    total_steel_cost,
                    total_cement_cost,
                    total_budget * 0.35,
                    max(0, total_budget - (total_steel_cost + total_cement_cost + total_budget * 0.35))
                ]
            })
            fig_cost = px.pie(
                cost_dist_df,
                names="Category",
                values="Amount_INR",
                title="Budget Allocation by Trade",
                hole=0.45,
                color_discrete_sequence=["#FF6B00", "#3B82F6", "#10B981", "#94A3B8"]
            )
            fig_cost.update_layout(margin=dict(l=10, r=10, t=35, b=10), height=230)
            st.plotly_chart(fig_cost, use_container_width=True)

        # Download Planning Report
        st.markdown("##### 💾 Export Financial & Material Plan")
        plan_report_dict = {
            "project_name": "ConstructIQ Valuation & Planning Report",
            "timestamp": datetime.now().isoformat(),
            "inputs": {
                "structure_type": structure_type,
                "built_up_area_sqft": built_up_area,
                "location_tier": city_tier,
                "cost_per_sqft_inr": cost_per_sqft,
                "completion_pct": completion_pct
            },
            "financials": {
                "total_budget_inr": total_budget,
                "total_budget_formatted": format_inr(total_budget),
                "expenditure_to_date_inr": expenditure_to_date,
                "expenditure_to_date_formatted": format_inr(expenditure_to_date),
                "remaining_budget_inr": remaining_budget,
                "remaining_budget_formatted": format_inr(remaining_budget),
                "indicative_current_valuation_inr": indicative_current_valuation,
                "indicative_current_valuation_formatted": format_inr(indicative_current_valuation),
                "full_completed_market_value_inr": full_market_value,
                "full_completed_market_value_formatted": format_inr(full_market_value)
            },
            "materials_forecast": {
                "cement_50kg_bags": total_cement_bags,
                "cement_estimated_cost_inr": total_cement_cost,
                "cement_estimated_cost_formatted": format_inr(total_cement_cost),
                "steel_tonnes": total_steel_tonnes,
                "steel_kg": total_steel_kg,
                "steel_estimated_cost_inr": total_steel_cost,
                "steel_estimated_cost_formatted": format_inr(total_steel_cost),
                "sand_cu_ft": total_sand_cft,
                "coarse_aggregate_cu_ft": total_aggregate_cft
            },
            "disclaimer": "VALUATION DISCLAIMER: Calculations are indicative financial models based on standard civil engineering heuristics and regional market averages. They do not constitute guaranteed contractor bids or statutory real-estate appraisals."
        }

        st.download_button(
            label="⬇️ Download Planning & Valuation Report (JSON)",
            data=json.dumps(plan_report_dict, indent=2),
            file_name=f"Construction_Planning_Valuation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )


# =============================================================================
# FEATURE 4: DAILY SITE ASSISTANT & WEATHER ADVISORY
# =============================================================================
WEATHER_PRECAUTIONS = {
    "Normal": {
        "badge_color": "#10B981",
        "icon": "☀️",
        "summary": "Favorable environmental conditions. Standard site operating procedures active.",
        "precautions": [
            "Conduct routine 07:00 morning toolbox talk reviewing daily task hazards and PPE compliance.",
            "Verify perimeter fall arrest cabling at all slab edges > 6 ft elevation (OSHA 1926.501).",
            "Maintain standard tower crane and hoist operations with normal inspection log sign-off.",
            "Ensure concrete batching and curing schedules proceed per standard technical specifications."
        ]
    },
    "Heavy Rain": {
        "badge_color": "#3B82F6",
        "icon": "🌧️",
        "summary": "High precipitation risk: Electrical hazards, soil erosion, and excavation pit collapse risk.",
        "precautions": [
            "⚡ Electrical Isolation: Inspect all temporary 3-phase power distribution boards, ensure GFCI / ELCB breakers are functioning, and elevate all power cords above ground pooling water.",
            "🚜 Deep Excavation & Trenching: Immediately halt trench entry if water accumulation occurs. Deploy submersible dewatering pumps to avoid hydraulic soil slippage and trench cave-in.",
            "🧱 Concrete Pour Restrictions: Do not cast open slabs without rain protective tarping. Rainwater dilutes the water-cement ratio, drastically impairing 28-day compressive strength.",
            "🪜 Scaffolding Stability: Inspect base jacks and mudsills for soil softening or subsidence before allowing workers to mount scaffolding."
        ]
    },
    "High Wind": {
        "badge_color": "#EF4444",
        "icon": "💨",
        "summary": "CRITICAL CRANE & ELEVATION RISK: Gale-force gusts exceeding operational safety cutoffs.",
        "precautions": [
            "🚨 MANDATORY TOWER CRANE SUSPENSION: Wind speeds exceeding 38 km/h (20 knots / 10.5 m/s) require immediate suspension of all tower crane lifting operations per OSHA 1926.1431 & IS 13367.",
            "🏗️ Crane Weathervaning: Disengage slew brakes on tower cranes to permit the jib to freely weathervane with the wind direction, minimizing overturning moments.",
            "🛡️ High-Elevation Operations: Immediately halt all roofing, exterior facade glazing, and elevated steel erection.",
            "📦 Loose Material Securing: Fasten or lower all loose plywood, corrugated sheeting, and insulation bundles to prevent lethal falling-object hazards."
        ]
    },
    "Extreme Heat": {
        "badge_color": "#F59E0B",
        "icon": "🌡️",
        "summary": "Heatwave Conditions (>40°C / 104°F): Severe thermal concrete cracking and worker heat illness risk.",
        "precautions": [
            "💧 Concrete Curing Hydration: High evaporation rates induce rapid plastic shrinkage cracking. Apply continuous wet burlap ponding or membrane-forming curing compounds immediately post-finishing per ACI 308R.",
            "🕒 Pours Timing Shift: Shift heavy concrete deck pours to early morning (05:00 - 08:30) or late evening to manage peak hydration temperatures.",
            "🥤 Heat Illness Prevention (OSHA): Mandatory 15-minute shaded rest breaks every 2 hours; provide chilled electrolyte drinking water onsite.",
            "🌡️ Concrete Batching Controls: Monitor delivery temperatures (<32°C). Utilize chilled mixing water or liquid nitrogen dosing at the batching plant if necessary."
        ]
    }
}

def get_assistant_response(user_query: str, chat_history: list, weather: str, api_key: str, model_name: str) -> str:
    """Generate multi-turn construction assistant response via Gemini or rule-based engine."""
    q_lower = user_query.lower()

    if not api_key or not HAS_GEMINI_SDK:
        # High quality technical engineering knowledge base for DEMO MODE
        prefix = "**[DEMO / RULE-BASED ADVISORY]**\n\n"

        if "curing" in q_lower or "cement" in q_lower or "43" in q_lower or "53" in q_lower:
            return prefix + (
                "**Concrete Curing Protocols (IS 456 & ACI 308R):**\n\n"
                "1. **Duration:** Ordinary Portland Cement (OPC 43 & 53 grade) requires a minimum of **7 continuous days** of moist curing in standard conditions, extending to **10–14 days** under hot/dry weather.\n"
                "2. **Methods:** Ponding with water on horizontal slabs; wet hessian/burlap wrapping on vertical columns with daily dampening twice daily.\n"
                "3. **Strength Gain:** Uncured concrete loses up to **40%** of its potential 28-day compressive strength due to incomplete silicate hydration."
            )
        elif "crane" in q_lower or "wind" in q_lower or "speed" in q_lower or "cutoff" in q_lower:
            return prefix + (
                "**Tower Crane Wind Safety Thresholds (OSHA 1926.1431 & IS 13367):**\n\n"
                "• **Operating Cutoff:** All crane lifting operations must immediately cease when wind gusts reach **38 km/h (20 knots / 10.5 m/s)**.\n"
                "• **Storm Parking:** Disengage the mechanical slew pin/brake to allow the jib to free-slew (weathervane) with the wind vector.\n"
                "• **Manufacturer Variance:** Always check the specific Load Chart in the operator cabin, as large-panel forms act as sails and require lower operational cutoffs (often 25–30 km/h)."
            )
        elif "slump" in q_lower or "workability" in q_lower:
            return prefix + (
                "**Standard Concrete Slump Ranges (IS 1199 & ASTM C143):**\n\n"
                "• **Normal RCC Slabs & Beams:** 75 mm to 100 mm (Medium workability).\n"
                "• **Heavily Reinforced Structural Elements / Deep Piles:** 125 mm to 175 mm (High workability with superplasticizer).\n"
                "• **Mass Concrete / Pavement:** 25 mm to 50 mm (Low workability).\n"
                "• *Rule of thumb:* Never add uncontrolled site water to increase slump; use PCE-based chemical admixtures."
            )
        elif "excavation" in q_lower or "trench" in q_lower or "shoring" in q_lower:
            return prefix + (
                "**Excavation Pit & Trench Safety Checklist (OSHA 1926 Subpart P):**\n\n"
                "1. **Depth Threshold:** Any trench exceeding **5 feet (1.5 m)** in depth mandates an engineered protective system (sloping, benching, or trench shoring box).\n"
                "2. **Egress Points:** Ladders or ramps must be placed within **25 feet** of lateral travel for all personnel.\n"
                "3. **Spoil Pile Clearance:** Keep excavated soil piles and heavy machinery at least **2 feet (0.6 m)** back from the trench edge to prevent surcharge cave-ins."
            )
        else:
            return prefix + (
                f"Thank you for your inquiry: *\"{user_query}\"*\n\n"
                f"**Current Weather Context:** `{weather}`\n"
                "1. **Civil Engineering Standard:** Verify execution complies with IS 456 (Concrete) and IS 800 (Steel) specifications.\n"
                "2. **Jobsite Safety:** Review the weather advisory precautions above before commencing work in this bay.\n"
                "3. **Quality Assurance:** Ensure slump cone test and test cube casting (3 cubes per 50 m³ pour) are documented in today's site diary.\n\n"
                "*(Note: Connect your Gemini API Key in the left sidebar to unlock live interactive multimodal LLM field reasoning)*"
            )

    # LIVE AI MODE via Gemini
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        system_instructions = f"""You are ConstructIQ AI, a senior licensed Professional Engineer (PE) and Site Project Superintendent.
Current Site Weather Condition: {weather}.
Provide technical, actionable, concise, and safety-compliant advice citing relevant engineering codes (OSHA, IS 456, ACI 318) when appropriate.
Format your answer with clean Markdown bullet points and bold headers."""

        # Format chat history for context
        history_prompts = [system_instructions]
        for msg in chat_history[-6:]:
            history_prompts.append(f"{msg['role'].upper()}: {msg['content']}")
        history_prompts.append(f"USER: {user_query}")
        history_prompts.append("ASSISTANT:")

        response = model.generate_content("\n\n".join(history_prompts))
        return response.text
    except Exception as e:
        return f"Error communicating with Gemini Assistant: {str(e)}. (Reverted to rule-based engine)."


if app_section == "🌦️ 4. Daily Assistant & Weather Advisory":
    st.subheader("🌦️ Feature 4: Daily Site Assistant & Weather Advisory")
    st.caption("Site-specific meteorological safety advisories and a multi-turn construction engineering assistant chatbot.")

    col_w1, col_w2 = st.columns([1, 1.2], gap="large")

    with col_w1:
        st.markdown("#### 1. Site Meteorological Advisory")
        weather_choice = st.selectbox(
            "Select Current / Forecasted Jobsite Weather:",
            ["Normal", "Heavy Rain", "High Wind", "Extreme Heat"],
            index=2 # Default to High Wind to showcase critical crane safety protocols!
        )

        weather_info = WEATHER_PRECAUTIONS[weather_choice]

        # Weather Alert Box
        st.markdown(f"""
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 6px solid {weather_info['badge_color']}; padding: 1rem 1.2rem; border-radius: 8px; margin-bottom: 1.2rem;">
            <h4 style="margin: 0; color: #0F172A;">{weather_info['icon']} Weather Condition: {weather_choice}</h4>
            <p style="margin: 0.4rem 0 0 0; color: #475569; font-size: 0.92rem;">{weather_info['summary']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("##### ⚠️ Mandatory Weather-Specific Safety Precautions")
        for p in weather_info["precautions"]:
            st.markdown(f"- {p}")

        if weather_choice == "High Wind":
            st.error("🚨 **CRITICAL WARNING:** Tower Crane operations prohibited above 38 km/h. Disengage slew brakes to permit weathervaning.")
        elif weather_choice == "Heavy Rain":
            st.warning("⚡ **ELECTRICAL & TRENCH WARNING:** Isolate all open 3-phase DBs and inspect excavation walls for hydraulic erosion.")
        elif weather_choice == "Extreme Heat":
            st.warning("💧 **CONCRETE CURING WARNING:** Immediate wet burlap ponding required post-pour to prevent plastic shrinkage cracking.")

    with col_w2:
        st.markdown("#### 2. Multi-Turn Field Engineering Assistant")

        # Initialize chatbot history
        if "assistant_chat_history" not in st.session_state:
            st.session_state["assistant_chat_history"] = [
                {
                    "role": "assistant",
                    "content": "Hello! I am your **ConstructIQ Site Engineering Assistant**. Ask me about concrete curing protocols, tower crane wind safety limits, excavation shoring, or slump test standards."
                }
            ]

        # Quick preset buttons for common engineering questions
        st.markdown("**Quick Technical Inquiries:**")
        b1, b2 = st.columns(2)
        q1 = b1.button("💨 Tower crane wind speed cutoff")
        q2 = b2.button("💧 43-Grade cement curing protocol")
        q3 = b1.button("🧱 Slump test standard for slabs")
        q4 = b2.button("🚜 Deep excavation trench safety")

        preset_query = None
        if q1:
            preset_query = "What is the maximum permissible wind speed for operating a tower crane on a construction site?"
        elif q2:
            preset_query = "What is the recommended curing duration and method for 43-grade Ordinary Portland Cement?"
        elif q3:
            preset_query = "What is the acceptable concrete slump test range for casting reinforced suspended slabs?"
        elif q4:
            preset_query = "What are the essential OSHA safety precautions when excavating trenches deeper than 5 feet?"

        # Chat display container
        chat_box = st.container(height=360)
        with chat_box:
            for message in st.session_state["assistant_chat_history"]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        user_input = st.chat_input("Ask a civil engineering or site safety question...")
        active_query = user_input or preset_query

        if active_query:
            # Display user query
            st.session_state["assistant_chat_history"].append({"role": "user", "content": active_query})
            with chat_box:
                with st.chat_message("user"):
                    st.markdown(active_query)

            # Generate and display assistant reply
            with chat_box:
                with st.chat_message("assistant"):
                    with st.spinner("Consulting engineering specifications and weather safety rules..."):
                        bot_reply = get_assistant_response(
                            user_query=active_query,
                            chat_history=st.session_state["assistant_chat_history"],
                            weather=weather_choice,
                            api_key=active_key if is_live_mode else "",
                            model_name=model_choice
                        )
                        st.markdown(bot_reply)

            st.session_state["assistant_chat_history"].append({"role": "assistant", "content": bot_reply})

        if st.button("🗑️ Clear Chat"):
            st.session_state["assistant_chat_history"] = [
                {"role": "assistant", "content": "Chat history cleared. What can I help you analyze on site today?"}
            ]
            st.rerun()

# -----------------------------------------------------------------------------
# GLOBAL FOOTER
# -----------------------------------------------------------------------------
st.markdown("---")
f_col1, f_col2 = st.columns([2, 1])
with f_col1:
    st.caption("🏗️ **ConstructIQ: Multimodal Construction Intelligence Platform** • Skill Wallet Capstone Project")
    st.caption("Standards Implemented: **OSHA 1926 (Safety)** &bull; **ACI 224R (Concrete Cracks)** &bull; **IS 456 / IS 800 (Civil & Structural Codes)**")
with f_col2:
    st.caption(f"Status: **{'🟢 LIVE AI MODE' if is_live_mode else '🟡 DEMO MODE (Heuristic Engine)'}**")
    st.caption("Built with Streamlit & Google Gemini Multimodal SDK")
