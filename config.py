"""
Configuration module for Multimodal Construction Intelligence Platform.
Centralizes constants, OSHA safety standards, Gemini model definitions, and environment settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
SAMPLE_IMAGES_DIR = ASSETS_DIR / "sample_images"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
SAMPLE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Load .env if present
load_dotenv(BASE_DIR / ".env")

# App Metadata
APP_NAME = "ConstructIQ"
APP_SUBTITLE = "Multimodal Construction Intelligence & Site Safety AI Platform"
APP_VERSION = "v1.0.0 Pro"

# Gemini Models
AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-1.5-flash",
    "gemini-1.5-pro"
]
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")

# Construction Zones Configuration
SITE_ZONES = {
    "Zone A": {
        "name": "Zone A - Tower Crane Swing Radius",
        "risk_level": "CRITICAL",
        "description": "Overhead suspended load hazard. Strict hardhat, hi-vis vest, and radio clearance required.",
        "color": "#EF4444"  # Red
    },
    "Zone B": {
        "name": "Zone B - Deep Excavation Pit",
        "risk_level": "HIGH",
        "description": "Cave-in and fall hazard (>2m depth). Trench shoring and edge barriers active.",
        "color": "#F59E0B"  # Amber
    },
    "Zone C": {
        "name": "Zone C - Structural Steel Erection",
        "risk_level": "HIGH",
        "description": "Working at elevation (>6ft). Fall arrest harnesses and steel-toe boots mandatory.",
        "color": "#3B82F6"  # Blue
    },
    "Zone D": {
        "name": "Zone D - Material Staging & Delivery",
        "risk_level": "MODERATE",
        "description": "Forklift and telehandler traffic. High-visibility vests mandatory at all times.",
        "color": "#10B981"  # Emerald
    }
}

# Required PPE items and OSHA regulations
PPE_REGULATIONS = {
    "hardhat": {
        "label": "Hard Hat / Safety Helmet",
        "regulation": "OSHA 1926.100 (Head Protection)",
        "color": "#FACC15"
    },
    "hi_vis_vest": {
        "label": "High-Visibility Vest",
        "regulation": "OSHA 1926.201 / ANSI 107 (High-Visibility Safety Apparel)",
        "color": "#4ADE80"
    },
    "safety_boots": {
        "label": "Steel-Toe Safety Boots",
        "regulation": "OSHA 1926.96 (Occupational Foot Protection)",
        "color": "#94A3B8"
    },
    "gloves": {
        "label": "Cut-Resistant Work Gloves",
        "regulation": "OSHA 1926.95 (Hand Protection)",
        "color": "#A78BFA"
    },
    "fall_harness": {
        "label": "Fall Arrest Harness",
        "regulation": "OSHA 1926.501 (Fall Protection at Elevation)",
        "color": "#F43F5E"
    }
}

# Milestone schedule baseline
PROJECT_MILESTONES = [
    {"phase": "Site Prep & Excavation", "planned_pct": 100, "actual_pct": 100, "status": "Completed"},
    {"phase": "Deep Foundation & Piles", "planned_pct": 100, "actual_pct": 100, "status": "Completed"},
    {"phase": "Substructure Concrete Pour", "planned_pct": 95, "actual_pct": 92, "status": "On Track"},
    {"phase": "Superstructure Steel Framing", "planned_pct": 75, "actual_pct": 68, "status": "Minor Delay"},
    {"phase": "Curtain Wall & Facade Glazing", "planned_pct": 45, "actual_pct": 36, "status": "Attention Needed"},
    {"phase": "MEP (Mechanical/Electrical/Plumbing)", "planned_pct": 35, "actual_pct": 30, "status": "On Track"},
    {"phase": "Interior Drywall & Finishes", "planned_pct": 15, "actual_pct": 10, "status": "Scheduled"},
    {"phase": "Commissioning & Closeout", "planned_pct": 0, "actual_pct": 0, "status": "Scheduled"}
]

def get_api_key(session_key: str = None) -> str:
    """Retrieve Gemini API key from session or environment."""
    if session_key and session_key.strip():
        return session_key.strip()
    return os.getenv("GEMINI_API_KEY", "").strip()
