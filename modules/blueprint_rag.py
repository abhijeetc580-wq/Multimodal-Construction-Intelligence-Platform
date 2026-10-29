"""
Multimodal Blueprint & Document RAG Field Assistant.
Enables natural language Q&A, architectural drawing inspection, specification grounding,
and automated RFI drafting using Gemini Multimodal VLM and PDF extraction.
"""

from pathlib import Path
from PIL import Image
import streamlit as st
import pypdf
from utils.gemini_client import ask_blueprint_assistant
from config import SAMPLE_IMAGES_DIR

# Sample technical specifications embedded into the construction corpus
SAMPLE_SPECS_TEXT = """
[PROJECT SPECIFICATION - SECTION 03-3000: CAST-IN-PLACE CONCRETE]
1. COMPRESSIVE STRENGTH:
   - Footings, Grade Beams, and Foundation Piers: f'c = 4,500 psi minimum at 28 days.
   - Elevated Post-Tensioned Suspended Slabs: f'c = 5,000 psi minimum at 28 days.
   - Interior Non-Structural Topping Slabs: f'c = 3,000 psi minimum at 28 days.
2. REINFORCEMENT:
   - Deformed Steel Bars: ASTM A615 Grade 60.
   - Welded Wire Fabric: ASTM A1064.
   - Concrete Clear Cover: 3.0 inches where cast against earth; 1.5 inches for interior formed beams.
3. CURING:
   - Moist cure for a minimum period of 7 continuous days per ACI 308.1.

[PROJECT SPECIFICATION - SECTION 08-1100: HOLLOW METAL DOORS & FRAMES]
1. FIRE RATINGS:
   - East and West Egress Stairwell Enclosures: 2-Hour Fire-Resistance Rating per IBC Section 1023.2.
   - Doors in 2-Hour Stairwells: 90-minute UL-labeled B-Label hollow metal fire doors.
   - Hardware: Self-closing panic exit devices with magnetic hold-open releases integrated with site fire alarm.

[PROJECT SPECIFICATION - SECTION 23-0000: HVAC & SLAB PENETRATIONS]
1. SLAB DROP PANELS:
   - No penetrations or sleeves larger than 4 inches diameter shall be placed within 24 inches of column drop panels without written approval from Structural Engineer of Record (SEOR).
"""

def render_blueprint_tab(api_key: str, model_name: str):
    st.markdown("### 📐 Multimodal Blueprint & Field RAG Assistant")
    st.caption("Ask questions, audit drawings, verify code compliance, and draft RFIs grounded in architectural CAD blueprints and technical specifications.")

    col_doc, col_chat = st.columns([1, 1], gap="medium")

    with col_doc:
        st.subheader("Architectural Drawing & Document Corpus")
        doc_mode = st.radio(
            "Blueprint / Spec Source:",
            ["Demo: Apex Tower Level 2 Plan (DWG A-102)", "Upload Custom Blueprint (PNG, JPG, PDF)"],
            index=0
        )

        blueprint_img = None
        blueprint_path = SAMPLE_IMAGES_DIR / "sample_blueprint.png"

        if doc_mode == "Demo: Apex Tower Level 2 Plan (DWG A-102)":
            if not blueprint_path.exists():
                from modules.mock_data import generate_sample_blueprint
                blueprint_img = generate_sample_blueprint(blueprint_path)
            else:
                blueprint_img = Image.open(blueprint_path)
            st.image(blueprint_img, caption="DWG NO: A-102 | Apex Tower Level 2 Architectural Plan", use_container_width=True)
            doc_context = SAMPLE_SPECS_TEXT
        else:
            uploaded_doc = st.file_uploader("Upload Blueprint or Spec (PNG, JPG, PDF)", type=["png", "jpg", "jpeg", "pdf"])
            doc_context = SAMPLE_SPECS_TEXT
            if uploaded_doc is not None:
                if uploaded_doc.name.endswith(".pdf"):
                    try:
                        reader = pypdf.PdfReader(uploaded_doc)
                        extracted = "\n".join([page.extract_text() or "" for page in reader.pages[:10]])
                        doc_context += f"\n\n[USER UPLOADED PDF SPEC]:\n{extracted}"
                        st.success(f"Extracted {len(reader.pages)} pages from uploaded PDF.")
                    except Exception as e:
                        st.error(f"Error parsing PDF: {e}")
                else:
                    blueprint_img = Image.open(uploaded_doc)
                    st.image(blueprint_img, caption="Uploaded Architectural Drawing", use_container_width=True)
            elif blueprint_path.exists():
                blueprint_img = Image.open(blueprint_path)

        with st.expander("📖 Active Grounded Specifications Knowledge Base", expanded=False):
            st.text_area("Specification Excerpts:", doc_context, height=180, disabled=True)

    with col_chat:
        st.subheader("Field AI Engineer Chat")
        
        # Initialize chat history
        if "blueprint_chat_history" not in st.session_state:
            st.session_state["blueprint_chat_history"] = [
                {
                    "role": "assistant",
                    "content": "Hello! I am your Multimodal Field Engineering Assistant. Ask me to verify dimensions, check fire ratings, cite concrete specs, or draft an RFI."
                }
            ]

        # Quick Prompt Chips
        st.markdown("**Quick Prompts:**")
        q_cols = st.columns(2)
        p1 = q_cols[0].button("🔥 Check stairwell fire ratings")
        p2 = q_cols[1].button("📝 Draft RFI for slab penetration clash")
        p3 = q_cols[0].button("🏗️ Concrete compressive specs")
        p4 = q_cols[1].button("🚪 ADA corridor width requirements")

        user_input_preset = None
        if p1:
            user_input_preset = "What is the fire rating requirement for the East and West stairwells and their door assemblies?"
        elif p2:
            user_input_preset = "Draft an urgent RFI to the lead structural engineer regarding a 24x18 HVAC duct penetration near Column C-4."
        elif p3:
            user_input_preset = "What is the required 28-day compressive strength and minimum clear cover for foundation footings and suspended slabs?"
        elif p4:
            user_input_preset = "Verify if the central circulation corridor width on Level 2 meets the minimum egress clearance standards."

        # Render chat messages
        chat_container = st.container(height=380)
        with chat_container:
            for msg in st.session_state["blueprint_chat_history"]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Chat input box
        prompt = st.chat_input("Ask a question about the blueprint or specifications...")
        query_to_run = prompt or user_input_preset

        if query_to_run:
            # Append user message
            st.session_state["blueprint_chat_history"].append({"role": "user", "content": query_to_run})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(query_to_run)

            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing drawing vectors and consulting specifications..."):
                        response = ask_blueprint_assistant(
                            question=query_to_run,
                            blueprint_image=blueprint_img,
                            document_text=doc_context,
                            chat_history=st.session_state["blueprint_chat_history"],
                            model_name=model_name,
                            api_key=api_key
                        )
                        st.markdown(response)

            st.session_state["blueprint_chat_history"].append({"role": "assistant", "content": response})

        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state["blueprint_chat_history"] = [
                {"role": "assistant", "content": "Chat history cleared. How can I assist you with the blueprints?"}
            ]
            st.rerun()
