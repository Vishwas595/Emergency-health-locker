import streamlit as st
import requests
from datetime import date

from utils.qr_generator import (
    generate_emergency_qr,
    get_public_link,
    get_nfc_instructions
)
from utils.pdf_generator import generate_medical_pdf
from utils.file_parser import extract_text_from_file
from utils.medical_mapper import map_medical_data

# ===============================
# CONFIG
# ===============================
st.set_page_config(
    page_title="User Dashboard",
    page_icon="👤",
    layout="wide"
)

API_BASE = "https://emergency-health-locker.onrender.com/api"

st.title("👤 User Dashboard")
st.markdown("### View / Upload Your Medical Information")
st.divider()

# ===============================
# MODE SELECTION
# ===============================
st.subheader("🧭 Select Action")

mode = st.radio(
    "What do you want to do?",
    ["➕ Add New Patient", "✏️ Update Existing Patient"]
)

# ===============================
# FILE UPLOAD
# ===============================
st.divider()
st.header("📤 Upload Medical Record (Optional)")

uploaded_file = st.file_uploader(
    "Upload medical report (PDF / Image)",
    type=["pdf", "png", "jpg", "jpeg"]
)

auto_data = {}

if uploaded_file:
    with st.spinner("Reading medical document..."):
        extracted_text = extract_text_from_file(uploaded_file)

    if extracted_text:
        st.subheader("📄 Extracted Text (Review)")
        st.text_area("Detected text", extracted_text, height=220)

        auto_data = map_medical_data(extracted_text)
        st.success("✅ Medical data auto-detected")

# ===============================
# PATIENT ID
# ===============================
st.divider()
st.header("🆔 Patient Identification")

patient = {}

if mode == "➕ Add New Patient":
    st.info("🆕 Creating a NEW patient")
    patient_id = st.text_input("Enter NEW Patient ID", placeholder="e.g., P253")

else:
    st.info("🔄 Updating EXISTING patient")
    patient_id = st.text_input("Enter Existing Patient ID", placeholder="e.g., P001")

    if patient_id:
        r = requests.get(f"{API_BASE}/patients/{patient_id}")
        if r.status_code == 200:
            patient = r.json()
            st.success("✅ Patient loaded")
        else:
            st.error("❌ Patient not found")
            patient = {}

# ===============================
# FORM
# ===============================
st.divider()
st.header("✏️ Review & Update Details")

with st.form("user_form"):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            "Full Name",
            value=auto_data.get("Name") or patient.get("Name", "")
        )

        dob_raw = patient.get("Date_of_Birth")
        dob = st.date_input(
            "Date of Birth",
            value=date.fromisoformat(dob_raw) if dob_raw else None,
            min_value=date(1900, 1, 1),
            max_value=date.today()
        )

        gender = st.selectbox(
            "Gender",
            ["Male", "Female", "Other"],
            index=0
        )

        blood_groups = ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        default_bg = auto_data.get("Blood_Group") or patient.get("Blood_Type", "")
        blood = st.selectbox(
            "Blood Group",
            blood_groups,
            index=blood_groups.index(default_bg) if default_bg in blood_groups else 0
        )

    with col2:
        emergency_contact = st.text_input(
            "Emergency Contact",
            value=patient.get("Emergency_Contacts", "")
        )

        meds = st.text_area(
            "Current Medications",
            value=patient.get("Current_Medications", "")
        )

        drug_all = st.text_area(
            "Drug Allergies",
            value=patient.get("Drug_Allergies", "")
        )

        surg = st.text_area(
            "Recent Surgeries",
            value=patient.get("Recent_Surgeries", "")
        )

    emergency_status = st.text_input(
        "Emergency Alert / Condition",
        value=patient.get("Emergency_Status", "")
    )

    lab_findings = st.text_area(
        "Recent Lab Findings",
        value=(
            f"HbA1c: {auto_data.get('HbA1c','')}\n"
            f"Fasting Sugar: {auto_data.get('Fasting_Sugar','')}"
        ).strip() or patient.get("Recent_Lab_Findings", "")
    )

    submit = st.form_submit_button("✅ Save Patient Data")

    if submit:
        if not patient_id:
            st.error("❌ Patient ID is required")
        else:
            payload = {
                "Patient_ID": patient_id,
                "Name": name,
                "Date_of_Birth": dob.isoformat() if dob else "",
                "Gender": gender,
                "Blood_Type": blood,
                "Emergency_Contacts": emergency_contact,
                "Current_Medications": meds,
                "Drug_Allergies": drug_all,
                "Recent_Surgeries": surg,
                "Emergency_Status": emergency_status,
                "Recent_Lab_Findings": lab_findings
            }

            r = requests.post(f"{API_BASE}/user/patients", json=payload)
            if r.status_code in [200, 201]:
                st.success("🎉 Patient data saved!")
                patient = payload
            else:
                st.error(r.text)

# ===============================
# QR & PDF
# ===============================
if patient_id and patient:
    st.divider()
    st.header("🔳 Emergency Access")

    qr = generate_emergency_qr(patient_id)
    st.image(qr, width=250)

    st.code(get_public_link(patient_id))
    st.markdown(get_nfc_instructions())

    pdf = generate_medical_pdf(patient)
    st.download_button(
        "📄 Download Medical PDF",
        pdf,
        file_name=f"Medical_{patient_id}.pdf",
        mime="application/pdf"
    )

st.caption("Emergency Health Locker • User Module • Phase 2A ✅ COMPLETE")
