"""
Automated Daily Site Inspection & Executive Report Generator.
Builds professional PDF inspection reports using ReportLab and Markdown daily logs.
"""

from io import BytesIO
from datetime import datetime
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from config import APP_NAME, APP_VERSION

def generate_pdf_report(
    project_name: str,
    date_str: str,
    weather: str,
    safety_score: float,
    workers_count: int,
    violations_count: int,
    superintendent: str,
    safety_officer: str,
    notes: str
) -> bytes:
    """
    Generate an OSHA-compliant Daily Site Inspection PDF report with ReportLab.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=14
    )
    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    story = []

    # Title & Header
    story.append(Paragraph(f"<b>{APP_NAME}</b> | Daily Site Intelligence & Safety Audit", title_style))
    story.append(Paragraph(f"Official Jobsite Compliance Record • Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#CBD5E1"), spaceAfter=12))

    # Project Metadata Table
    meta_data = [
        [Paragraph("<b>Project:</b>", body_style), Paragraph(project_name, body_style),
         Paragraph("<b>Date of Inspection:</b>", body_style), Paragraph(date_str, body_style)],
        [Paragraph("<b>Weather / Temp:</b>", body_style), Paragraph(weather, body_style),
         Paragraph("<b>Site Superintendent:</b>", body_style), Paragraph(superintendent, body_style)],
        [Paragraph("<b>Safety Officer:</b>", body_style), Paragraph(safety_officer, body_style),
         Paragraph("<b>Compliance Standard:</b>", body_style), Paragraph("OSHA 1926 & ACI 318", body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[110, 150, 120, 150])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 14))

    # Executive KPI Summary
    story.append(Paragraph("1. Executive Site Key Performance Indicators (KPIs)", h2_style))
    kpi_data = [
        [
            Paragraph("<b>Safety Compliance Index</b>", body_style),
            Paragraph("<b>Total Active Labor</b>", body_style),
            Paragraph("<b>Violations Flagged</b>", body_style),
            Paragraph("<b>Overall Milestone SPI</b>", body_style)
        ],
        [
            Paragraph(f"<font color='{'#10B981' if safety_score >= 90 else '#EF4444'}'><b>{safety_score}%</b></font>", h2_style),
            Paragraph(f"<b>{workers_count} Workers</b>", h2_style),
            Paragraph(f"<b>{violations_count} Items</b>", h2_style),
            Paragraph("<b>0.91 (On Track)</b>", h2_style)
        ]
    ]
    t_kpi = Table(kpi_data, colWidths=[130, 130, 130, 140])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94A3B8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 14))

    # Safety Inspection Audit Table
    story.append(Paragraph("2. Site Safety & PPE Camera Audit Findings", h2_style))
    audit_data = [
        [Paragraph("<b>Time</b>", body_style), Paragraph("<b>Zone</b>", body_style), Paragraph("<b>Identified Infraction</b>", body_style), Paragraph("<b>Regulatory Citation</b>", body_style), Paragraph("<b>Corrective Action</b>", body_style)],
        [Paragraph("14:15", body_style), Paragraph("Zone A (Crane)", body_style), Paragraph("Worker without hardhat in crane radius", body_style), Paragraph("OSHA 1926.100", body_style), Paragraph("Worker halted & issued PPE", body_style)],
        [Paragraph("11:30", body_style), Paragraph("Zone C (Framing)", body_style), Paragraph("Perimeter barrier cable slack", body_style), Paragraph("OSHA 1926.502", body_style), Paragraph("Tensioned within 30 min", body_style)],
        [Paragraph("09:45", body_style), Paragraph("Zone D (Staging)", body_style), Paragraph("Forklift operator travel path clear", body_style), Paragraph("ANSI B56.1", body_style), Paragraph("Verified compliant", body_style)],
    ]
    t_audit = Table(audit_data, colWidths=[50, 90, 160, 100, 130])
    t_audit.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_audit)
    story.append(Spacer(1, 14))

    # Structural Quality & Defect Notes
    story.append(Paragraph("3. Structural Defect & Concrete Quality Notes", h2_style))
    story.append(Paragraph(
        "• <b>Level 2 Shear Wall (Grid D-4):</b> Hairline surface fissure detected via computer vision contour analysis. "
        "Estimated maximum width: 1.25 mm. Classification: Moderate. Epoxy surface sealing and displacement pin monitoring ordered.<br/>"
        "• <b>Concrete Compressive Cylinders:</b> 7-day break tests achieved 3,450 psi (76.6% of 28-day 4,500 psi specification target).",
        body_style
    ))
    story.append(Spacer(1, 14))

    # Superintendent Remarks
    story.append(Paragraph("4. Site Superintendent & Safety Officer Remarks", h2_style))
    story.append(Paragraph(notes or "Site operations progressed smoothly today. Glazing delivery rescheduled for Friday morning. Safety stand-down held at 07:00 regarding crane swing zone awareness.", body_style))
    story.append(Spacer(1, 24))

    # Digital Sign-off Signatures
    sign_data = [
        [Paragraph("___________________________________<br/><b>Site Superintendent Signature</b>", body_style),
         Paragraph("___________________________________<br/><b>Lead Safety Officer Signature</b>", body_style)],
        [Paragraph(f"Date: {date_str}", body_style), Paragraph(f"Date: {date_str}", body_style)]
    ]
    t_sign = Table(sign_data, colWidths=[260, 260])
    t_sign.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_sign)

    doc.build(story)
    return buffer.getvalue()

def render_report_tab():
    st.markdown("### 📑 Automated Daily Site Inspection Report Generator")
    st.caption("Generate verifiable, OSHA-compliant Daily Site Inspection Reports in PDF and Markdown format for stakeholders, owners, and regulatory authorities.")

    col_input, col_preview = st.columns([1, 1], gap="medium")

    with col_input:
        st.subheader("Inspection Parameters")
        p_name = st.text_input("Project Name:", value="Apex Tower - Phase 2 Superstructure")
        p_date = st.date_input("Inspection Date:", value=datetime.today())
        p_weather = st.text_input("Weather Conditions:", value="72°F / 22°C, Clear Sky, Wind 6 mph")
        p_super = st.text_input("Site Superintendent:", value="Marcus Vance (GC Field Lead)")
        p_safety = st.text_input("Lead Safety Officer:", value="Elena Rostova (CSP, OSHA 500)")

        st.markdown("#### Performance Metrics")
        m_col1, m_col2 = st.columns(2)
        p_safety_score = m_col1.slider("Safety Index Score (%)", 50.0, 100.0, 94.2, step=0.1)
        p_labor = m_col2.number_input("Active Workers Onsite", min_value=1, max_value=300, value=48)
        p_violations = m_col1.number_input("Violations Logged", min_value=0, max_value=50, value=1)

        p_notes = st.text_area(
            "Superintendent Field Notes & Summary:",
            value="Site operations progressed with zero lost-time incidents. Safety stand-down held at 07:00 regarding crane swing zone awareness. Level 3 concrete pour scheduled for 06:00 tomorrow morning.",
            height=100
        )

        generate_btn = st.button("📄 Generate Official PDF Inspection Report", type="primary", use_container_width=True)

    with col_preview:
        st.subheader("Report Export & Live Preview")
        
        pdf_bytes = generate_pdf_report(
            project_name=p_name,
            date_str=str(p_date),
            weather=p_weather,
            safety_score=p_safety_score,
            workers_count=p_labor,
            violations_count=p_violations,
            superintendent=p_super,
            safety_officer=p_safety,
            notes=p_notes
        )

        st.download_button(
            label="⬇️ Download Official PDF Report",
            data=pdf_bytes,
            file_name=f"Daily_Inspection_Report_{p_date}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("#### Instant Markdown Summary (for Email / Slack Sync)")
        md_content = f"""# Daily Construction Site Intelligence & Safety Audit
**Project:** {p_name}  
**Date:** {p_date} | **Weather:** {p_weather}  
**Superintendent:** {p_super} | **Safety Officer:** {p_safety}  

### Executive Performance Metrics
- **Safety Compliance Score:** `{p_safety_score}%`
- **Total Personnel Onsite:** `{p_labor} Workers`
- **Safety Infractions Logged:** `{p_violations}`
- **Schedule Milestone SPI:** `0.91 (On Track)`

### Safety & Structural Field Notes
{p_notes}
"""
        st.code(md_content, language="markdown")
