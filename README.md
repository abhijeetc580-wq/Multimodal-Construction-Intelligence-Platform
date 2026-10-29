# 🏗️ ConstructIQ: Multimodal Construction Intelligence Platform
### Skill Wallet Capstone Project

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini API](https://img.shields.io/badge/Google%20Gemini-Multimodal%20VLM-8E75C2.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![OSHA & IS Standards](https://img.shields.io/badge/Compliance-OSHA%201926%20%7C%20IS%20456%20%7C%20ACI%20224R-10B981.svg)]()

**ConstructIQ** is an enterprise-grade AI software platform engineered for construction site superintendents, project managers, and civil structural engineers. It combines **Google Gemini Multimodal Vision-Language Models (VLMs)**, domain-grounded civil engineering heuristics, and real-time interactive dashboards to automate jobsite safety auditing, structural crack diagnostics, localized construction budgeting, and meteorological safety warnings.

---

## 🌟 Key Platform Features

### 🦺 1. Site Safety & PPE Audit (OSHA 1926 Aligned)
* **Image Input:** Upload site photos in `JPG`, `JPEG`, or `PNG` format, or load pre-configured test frames.
* **Equipment Verification:** Automatically verifies helmets/hard hats (*OSHA 1926.100*), high-visibility safety vests (*ANSI/ISEA 107*), safety boots (*OSHA 1926.96*), and fall arrest harnesses (*OSHA 1926.501*).
* **Scoring & Hazard Classification:** Computes a Jobsite Safety Score (0–100), flags active hazards categorized across four severity levels (**Low, Medium, High, Critical**), and prescribes actionable corrective measures.
* **Exportable Reports:** Generates and downloads structured JSON inspection logs.
* **Honest Demo Mode:** When running without an API key, results are explicitly labeled as `[DEMO / SIMULATED AUDIT]` with clear disclaimers that simulated outputs are not actual image scans.

### 🔍 2. Structural Crack Diagnostics (ACI 224R Preliminary Assessment)
* **Defect Classification:** Classifies concrete and wall surface fissures into five standard engineering topologies:
  * **Hairline** (Non-structural drying shrinkage < 0.3 mm)
  * **Settlement** (Foundation subgrade differential displacement)
  * **Structural Shear** (45° diagonal tension failure)
  * **Thermal Expansion** (Cyclic temperature movement)
  * **Spalling** (Concrete delamination exposing corroded rebar)
* **Aperture & Urgency Assessment:** Estimates crack width in millimeters, identifies probable root causes, assigns urgency levels, and details a 4-step remediation protocol.
* **Downloadable JSON Output:** One-click export of diagnostic findings.
* **Mandatory Engineering Disclaimer:** Prominently states that preliminary image-based output cannot replace an in-person physical inspection by a licensed Professional Engineer (PE).

### 📊 3. Construction Planning & Real-Estate Valuation (Indian Economics in INR)
* **Regional Input Parameters:**
  * Structure Type: Residential High-Rise, Villa, Commercial Office, or Industrial Warehouse.
  * Built-Up Area in square feet ($sq. ft.$).
  * Indian City Tier: Tier 1 (Mumbai, Delhi-NCR, Bengaluru, Hyderabad, Pune, Chennai), Tier 2, or Tier 3.
  * Completion percentage (0% to 100%) and adjustable base construction cost per sq. ft.
* **Financial Calculations:**
  * Total project budget formatted in **Indian Crores and Lakhs (`₹`)**.
  * Cumulative expenditure incurred corresponding to progress.
  * Indicative current market property valuation factoring land equity and stage of completion.
* **Material Demand Forecasting (IS 456 Standards):**
  * Cement bag estimation (~0.42 bags of 50kg per sq. ft.).
  * Structural TMT steel rebar estimation (~4.0 kg per sq. ft.).
  * Coarse aggregate and sand (cu. ft.) requirements.
* **Interactive Controls:** All engineering coefficients and material unit prices are user-adjustable.

### 🌦️ 4. Daily Site Assistant & Weather Advisory
* **Meteorological Advisory Engine:**
  * **Normal:** Routine morning toolbox talks and standard PPE protocols.
  * **Heavy Rain:** Temporary electrical isolation, excavation sump pumping, and ban on open-air slab casting.
  * **High Wind:** **Mandatory Tower Crane Suspension Warning** (Wind speed cutoff > 38 km/h / 20 knots per OSHA 1926.1431 and IS 13367) and jib weathervaning directives.
  * **Extreme Heat (>40°C):** Continuous wet burlap curing directives (ACI 308R) to avoid plastic shrinkage cracking and mandatory worker hydration schedules.
* **Multi-Turn Civil Engineering Chatbot:**
  * Conversational memory for multi-turn dialogues.
  * Integrated with Google Gemini API when active, with graceful fallback to a domain-specific civil engineering knowledge base.
  * Quick-launch buttons for common site inquiries (crane cutoffs, cement curing duration, slump tests).

---

## 🛠️ Technology Stack

* **Language:** Python 3.10+
* **Frontend Framework:** Streamlit
* **Computer Vision & Imaging:** Pillow (PIL)
* **Data Processing:** pandas
* **Interactive Visualization:** Plotly
* **AI Engine:** Google Gemini API (`google-generativeai` SDK)
* **Database:** None required (Stateless session architecture, zero DB configuration needed)

---

## 🚀 Quickstart Guide

### 1. Clone & Navigate to Workspace
```powershell
cd C:\Users\abhij\OneDrive\Desktop\Multimodal-Construction-Intelligence-Platform
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run the Application
You can launch the platform using PowerShell or the included batch script:
```powershell
.\run.ps1
```
Or directly via Streamlit:
```powershell
streamlit run app.py
```
Open your browser at **`http://localhost:8501`**.

---

## 🔑 Mode Configuration (Live AI vs Demo Mode)

| Mode | API Key Required? | Status Indicator | Behavior |
| :--- | :--- | :--- | :--- |
| **DEMO MODE** | ❌ No | `🟡 DEMO MODE (SIMULATED AI)` | Fully functional out-of-the-box. Uses pre-calculated, deterministic engineering rules and sample datasets. Clearly labeled with demo disclaimers. |
| **LIVE AI MODE** | ✅ Yes | `🟢 LIVE AI MODE ACTIVE` | Performs live zero-shot multimodal image understanding and dynamic reasoning using Google Gemini models (`gemini-2.5-flash`, `gemini-1.5-pro`). |

To activate **Live AI Mode**, simply paste your Google Gemini API key into the secure password field in the sidebar or save it in a `.env` file:
```env
GEMINI_API_KEY=AIzaSy...
```

---

## 📂 Repository Structure

```
Multimodal-Construction-Intelligence-Platform/
├── app.py                      # Main Streamlit web application & feature logic
├── requirements.txt            # Production dependencies for local & cloud deploy
├── README.md                   # Complete platform documentation & run guide
├── PROJECT_REPORT.md           # Comprehensive Skill Wallet Capstone Technical Report
├── .gitignore                  # Git rules excluding secrets, cache, and virtualenvs
├── .env.example                # Environment variables template
├── run.ps1                     # PowerShell one-click launcher
├── run.bat                     # Windows CMD one-click launcher
├── sample_data/                # Sample JSON exports for audits and diagnostics
│   ├── sample_safety_audit.json
│   ├── sample_crack_diagnostic.json
│   └── sample_planning_valuation.json
└── assets/
    └── sample_images/          # Synthetic test images for 1-click feature verification
        ├── sample_site_safety.jpg
        └── sample_concrete_crack.jpg
```

---

## ☁️ Deployment on Streamlit Community Cloud

ConstructIQ is engineered to deploy seamlessly to **Streamlit Community Cloud** with zero system packages:
1. Push this repository to GitHub (ensure `.env` is ignored by `.gitignore`).
2. Log in to [share.streamlit.io](https://share.streamlit.io/).
3. Connect your repository and select `app.py` as the main file path.
4. (Optional) Add your `GEMINI_API_KEY` under **App Settings > Secrets**.
5. Click **Deploy**!

---

## 📜 Regulatory Standards Coded
* **OSHA 1926:** Safety and Health Regulations for Construction
* **ACI 224R-01:** Control of Cracking in Concrete Structures
* **IS 456:2000:** Indian Standard Code of Practice for Plain and Reinforced Concrete
* **IS 13367:** Code of Practice for Safe Use of Cranes
* **ANSI/ISEA 107:** High-Visibility Safety Apparel
