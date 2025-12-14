import streamlit as st
import requests
import re

from utils.qr_generator import (
    generate_emergency_qr,
    get_public_link,
    get_nfc_instructions
)
from utils.pdf_generator import generate_medical_pdf

# ===============================
# CONFIG
# ===============================
st.set_page_config(
    page_title="User Dashboard",
    page_icon="👤",
    layout="wide"
)

BACKEND_URL = "https://emergency-health-locker.onrender.com/api/patients"

st.title("👤 User Dashboard")
st.markdown("### View / Upload Your Medical Information")
st.divider()

# ===============================
# SAFE FILE PARSER IMPORT
# ===============================
try:
    from utils.file_parser import extract_text_from_file
    FILE_PARSER_AVAILABLE = True
except Exception:
    FILE_PARSER_AVAILABLE = False

# ===============================
# STEP A1: FILE UPLOAD
# ===============================
st.header("📤 Upload Medical Record (One-time optional)")

uploaded_file = st.file_uploader(
    "Upload medical report (PDF / Image)",
    type=["pdf", "png", "jpg", "jpeg"]
)

extracted_text = ""

if uploaded_file:
    st.success("✅ File uploaded successfully")
    st.write("Filename:", uploaded_file.name)

    if FILE_PARSER_AVAILABLE:
        with st.spinner("Reading medical document..."):
            extracted_text = extract_text_from_file(uploaded_file)

        st.subheader("📄 Extracted Text (Review)")
        st.text_area(
            "System detected the following text:",
            extracted_text,
            height=250
        )
    else:
        st.warning("⚠️ File parser not installed. Upload feature limited.")

# ===============================
# STEP A2: SIMPLE AUTO EXTRACTION
# ===============================
def auto_detect(patterns, text):
    for p in patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""

blood_type = auto_detect(
    [r"(A\+|A-|B\+|B-|AB\+|AB-|O\+|O-)"],
    extracted_text
)

drug_allergies = auto_detect(
    [r"allerg(y|ies)[:\- ]+([A-Za-z ,]+)"],
    extracted_text
)

medications = auto_detect(
    [r"medication(s)?[:\- ]+([A-Za-z0-9 ,mg]+)"],
    extracted_text
)

surgeries = auto_detect(
    [r"surgery|surgeries[:\- ]+([A-Za-z0-9 ,]+)"],
    extracted_text
)

# ===============================
# STEP B: PATIENT ID LOOKUP
# ===============================
st.divider()
st.header("🔍 Load Existing Profile")

col1, col2 = st.columns([3, 1])

with col1:
    patient_id = st.text_input(
        "Enter Your Patient ID",
        placeholder="e.g., P001"
    )

with col2:
    st.write("")
    search_btn = st.button("Get My Info", type="primary", use_container_width=True)

patient = None

if search_btn and patient_id:
    with st.spinner("Fetching your data..."):
        r = requests.get(f"{BACKEND_URL}/{patient_id}")
        if r.status_code == 200:
            patient = r.json()
            st.success("✅ Profile loaded")
        else:
            st.warning("No existing record found. You can create one.")

# ===============================
# STEP C: EDITABLE FORM (AUTO-FILLED)
# ===============================
st.divider()
st.header("✏️ Review & Update Your Details")

with st.form("user_edit_form"):
    colA, colB = st.columns(2)

    with colA:
        name = st.text_input(
            "Full Name",
            value=patient.get("Name", "") if patient else ""
        )
        dob = st.text_input(
            "Date of Birth",
            value=patient.get("Date_of_Birth", "") if patient else ""
        )
        gender = st.selectbox(
            "Gender",
            ["Male", "Female", "Other"],
            index=0
        )
        blood = st.text_input(
            "Blood Type",
            value=blood_type or (patient.get("Blood_Type", "") if patient else "")
        )

    with colB:
        emergency_contact = st.text_input(
            "Emergency Contact",
            value=patient.get("Emergency_Contacts", "") if patient else ""
        )
        meds = st.text_area(
            "Current Medications",
            value=medications or (patient.get("Current_Medications", "") if patient else "")
        )
        drug_all = st.text_area(
            "Drug Allergies",
            value=drug_allergies or (patient.get("Drug_Allergies", "") if patient else "")
        )
        surg = st.text_area(
            "Recent Surgeries",
            value=surgeries or (patient.get("Recent_Surgeries", "") if patient else "")
        )

    emergency_status = st.text_input(
        "Emergency Alert",
        value=patient.get("Emergency_Status", "") if patient else ""
    )

    submitted = st.form_submit_button("✅ Save / Update My Data")

    if submitted:
        payload = {
            "Patient_ID": patient_id,
            "Name": name,
            "Date_of_Birth": dob,
            "Gender": gender,
            "Blood_Type": blood,
            "Emergency_Contacts": emergency_contact,
            "Current_Medications": meds,
            "Drug_Allergies": drug_all,
            "Recent_Surgeries": surg,
            "Emergency_Status": emergency_status,
        }

        r = requests.post(BACKEND_URL, json=payload)
        if r.status_code in [200, 201]:
            st.success("🎉 Data saved successfully!")
        else:
            st.error("❌ Failed to save data")

# ===============================
# STEP D: QR / NFC / PDF
# ===============================
if patient_id:
    st.divider()
    st.header("🔳 QR Code & NFC")

    qr = generate_emergency_qr(patient_id)
    st.image(qr, width=280)

    st.download_button(
        "⬇️ Download QR Code",
        qr,
        file_name=f"QR_{patient_id}.png",
        mime="image/png"
    )

    public_link = get_public_link(patient_id)
    st.code(public_link)

    st.markdown(get_nfc_instructions())

    st.divider()
    st.header("📄 Download Medical PDF")

    pdf = generate_medical_pdf(payload if submitted else patient)
    st.download_button(
        "Download PDF",
        pdf,
        file_name=f"Medical_{patient_id}.pdf",
        mime="application/pdf"
    )

st.caption("Emergency Health Locker • User Module • Phase 1 Complete")
