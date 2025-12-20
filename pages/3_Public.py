import streamlit as st
import requests
from utils.pdf_generator import generate_medical_pdf

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Emergency Medical Information | QURE",
    page_icon="🚑",
    layout="wide"
)

# ===============================
# HIDE STREAMLIT UI ELEMENTS
# ===============================
st.markdown("""
<style>
header, footer, section[data-testid="stSidebar"] {
    display: none !important;
}
.block-container {
    padding-top: 0rem !important;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# CONSTANTS
# ===============================
API_BASE = "https://emergency-health-locker.onrender.com/api"

# ===============================
# HEADER
# ===============================
st.markdown("""
<style>
.emergency-header {
    background: #dc2626;
    color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div class="emergency-header">
        <h1>🚑 EMERGENCY MEDICAL INFORMATION</h1>
        <p>For Emergency Use Only</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ===============================
# GET PATIENT ID FROM URL
# ===============================
patient_id = st.query_params.get("patient_id")

if not patient_id:
    st.error("❌ Invalid access. Please scan the QR code or NFC card.")
    st.stop()

# ===============================
# SAFE API CALL (NO FREEZE)
# ===============================
with st.spinner("Loading emergency information..."):
    try:
        response = requests.get(
            f"{API_BASE}/public/{patient_id}",
            timeout=5   # ⬅️ critical
        )
    except requests.exceptions.RequestException:
        st.error("⚠️ Server is waking up. Please refresh after a few seconds.")
        st.stop()

if response.status_code != 200:
    st.error("❌ Unable to load emergency record.")
    st.stop()

patient = response.json()

# ===============================
# BASIC INFO
# ===============================
st.success(f"Emergency record loaded for **{patient.get('Name', 'Unknown')}**")
st.divider()

col1, col2, col3, col4 = st.columns(4)
col1.metric("PATIENT ID", patient.get("Patient_ID", "N/A"))
col2.metric("BLOOD GROUP", patient.get("Blood_Type", "N/A"))
col3.metric("DATE OF BIRTH", patient.get("Date_of_Birth", "N/A"))
col4.metric("GENDER", patient.get("Gender", "N/A"))

# ===============================
# EMERGENCY ALERT
# ===============================
if patient.get("Emergency_Status"):
    st.error(f"⚠️ **CRITICAL ALERT:** {patient['Emergency_Status']}")

st.divider()

# ===============================
# MEDICAL DETAILS
# ===============================
left, right = st.columns(2)

with left:
    st.markdown("### 🚨 Drug Allergies")
    st.info(patient.get("Drug_Allergies") or "None")

    st.markdown("### 💊 Current Medications")
    st.info(patient.get("Current_Medications") or "None")

    st.markdown("### 🏥 Recent Surgeries")
    st.info(patient.get("Recent_Surgeries") or "None")

with right:
    st.markdown("### 📞 Emergency Contact")
    st.info(patient.get("Emergency_Contacts") or "Not available")

    st.markdown("### 🔧 Medical Devices")
    st.info(patient.get("Medical_Devices") or "None")

    st.markdown("### 📊 Vital Signs")
    st.info(patient.get("Vital_Signs_Last_Recorded") or "Not recorded")

st.divider()

# ===============================
# PDF DOWNLOAD (SAFE)
# ===============================
try:
    pdf_bytes = generate_medical_pdf(patient)

    st.download_button(
        "📥 Download Complete Medical PDF",
        data=pdf_bytes,
        file_name=f"Emergency_Medical_{patient_id}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
except Exception as e:
    st.error("❌ Unable to generate PDF")

# ===============================
# FOOTER
# ===============================
st.warning("""
⚠️ **FOR EMERGENCY USE ONLY**

This information is provided to assist medical professionals.
Please verify with the patient whenever possible.
""")

st.caption("QURE • Emergency Access • v1.0")
