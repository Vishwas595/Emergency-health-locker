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
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="User Dashboard | QCURE",
    page_icon="👤",
    layout="wide"
)

# 🔒 HIDE SIDEBAR (USER SHOULD NOT SEE NAV)
st.markdown("""
<style>
section[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ===============================
# AUTH CHECK
# ===============================
if not st.session_state.get("logged_in") or st.session_state.get("role") != "USER":
    st.error("❌ Unauthorized access")
    st.stop()

# ===============================
# CORE VARIABLES
# ===============================
API_BASE = "https://emergency-health-locker.onrender.com/api"
PATIENT_ID = st.session_state.get("patient_id")

if not PATIENT_ID:
    st.error("❌ Session error: Patient ID missing")
    st.stop()

# ===============================
# HEADER
# ===============================
st.title("👤 User Dashboard")
st.markdown("### Manage Your Medical Information Securely")

# Logout
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("pages/0_Login.py")

st.divider()

# ===============================
# LOAD PATIENT DATA
# ===============================
patient = {}

with st.spinner("Loading your medical profile..."):
    res = requests.get(f"{API_BASE}/patients/{PATIENT_ID}")

if res.status_code == 200:
    patient = res.json()
else:
    st.error("❌ Unable to load patient data")
    st.stop()

# ===============================
# FILE UPLOAD (AUTO EXTRACTION)
# ===============================
st.header("📤 Upload Medical Report (Optional)")

uploaded_file = st.file_uploader(
    "Upload PDF or Image (for auto extraction)",
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
        st.success("✅ Medical data detected automatically")

st.divider()

# ===============================
# UPDATE MEDICAL PROFILE
# ===============================
st.header("✏️ Update Your Medical Profile")

with st.form("update_profile_form"):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Full Name", value=patient.get("Name", ""))

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
            index=["Male", "Female", "Other"].index(
                patient.get("Gender", "Male")
            )
        )

        blood_groups = ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        blood = st.selectbox(
            "Blood Group",
            blood_groups,
            index=blood_groups.index(
                patient.get("Blood_Type", "")
            ) if patient.get("Blood_Type") in blood_groups else 0
        )

    with col2:
        emergency_contact = st.text_input(
            "Emergency Contact",
            value=str(patient.get("Emergency_Contacts", ""))
        )

        medications = st.text_area(
            "Current Medications",
            value=patient.get("Current_Medications", "")
        )

        drug_allergies = st.text_area(
            "Drug Allergies",
            value=patient.get("Drug_Allergies", "")
        )

        other_allergies = st.text_area(
            "Other Allergies",
            value=patient.get("Other_Allergies", "")
        )

    surgeries = st.text_area(
        "Recent Surgeries",
        value=patient.get("Recent_Surgeries", "")
    )

    emergency_status = st.text_input(
        "Emergency Alert / Condition",
        value=patient.get("Emergency_Status", "")
    )

    vital_signs = st.text_input(
        "Last Recorded Vital Signs",
        value=patient.get("Vital_Signs_Last_Recorded", "")
    )

    devices = st.text_input(
        "Medical Devices",
        value=patient.get("Medical_Devices", "")
    )

    submit = st.form_submit_button("💾 Save Changes")

    if submit:
        payload = {
            "Patient_ID": PATIENT_ID,
            "Name": name,
            "Date_of_Birth": dob.isoformat() if dob else "",
            "Gender": gender,
            "Blood_Type": blood,
            "Emergency_Contacts": emergency_contact,
            "Current_Medications": medications,
            "Drug_Allergies": drug_allergies,
            "Other_Allergies": other_allergies,
            "Recent_Surgeries": surgeries,
            "Emergency_Status": emergency_status,
            "Vital_Signs_Last_Recorded": vital_signs,
            "Medical_Devices": devices
        }

        save = requests.post(
            f"{API_BASE}/user/patients",
            json=payload,
            timeout=10
        )

        if save.status_code in [200, 201]:
            st.success("✅ Profile updated successfully")
            st.rerun()
        else:
            st.error("❌ Failed to update profile")

# ===============================
# MEDICAL RECORDS (PHASE 2B)
# ===============================
st.divider()
st.header("📁 Your Medical Records")

st.subheader("📤 Upload New Record")

record_type = st.selectbox(
    "Record Type",
    ["Lab Report", "Prescription", "Medical Report", "Scan", "Other"]
)

record_title = st.text_input("Record Title")

record_file = st.file_uploader(
    "Upload PDF or Image",
    type=["pdf", "png", "jpg", "jpeg"],
    key="record_upload"
)

if st.button("⬆️ Upload Record"):
    if not record_title or not record_file:
        st.error("❌ Title and file are required")
    else:
        files = {
            "file": (record_file.name, record_file, record_file.type)
        }
        data = {
            "Patient_ID": PATIENT_ID,
            "Record_Type": record_type,
            "Record_Title": record_title,
            "Uploaded_By": "User"
        }

        res = requests.post(
            f"{API_BASE}/records/upload",
            files=files,
            data=data,
            timeout=15
        )

        if res.status_code == 201:
            st.success("✅ Medical record uploaded")
            st.rerun()
        else:
            st.error("❌ Upload failed")

# ===============================
# LIST MEDICAL RECORDS
# ===============================
st.subheader("📂 Uploaded Records")

records_res = requests.get(
    f"{API_BASE}/records/{PATIENT_ID}",
    timeout=10
)

if records_res.status_code == 200:
    records = records_res.json()

    if not records:
        st.info("No records uploaded yet.")
    else:
        for r in records:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{r['Record_Title']}**")
                st.caption(
                    f"{r['Record_Type']} • {r['File_Name']}"
                )
            with col2:
                st.markdown(
                    f"[⬇️ Download]"
                    f"({API_BASE}/records/download/{r['_id']})",
                    unsafe_allow_html=True
                )
            st.divider()
else:
    st.error("❌ Unable to load records")

# ===============================
# QR & EMERGENCY PDF
# ===============================
st.divider()
st.header("🚑 Emergency Access")

st.image(
    generate_emergency_qr(PATIENT_ID),
    width=240
)

st.code(get_public_link(PATIENT_ID))
st.markdown(get_nfc_instructions())

pdf = generate_medical_pdf(patient)

st.download_button(
    "📄 Download Complete Medical PDF",
    pdf,
    file_name=f"Medical_{PATIENT_ID}.pdf",
    mime="application/pdf"
)

st.divider()
st.caption("QURE • User Module • Secure Patient Access")
