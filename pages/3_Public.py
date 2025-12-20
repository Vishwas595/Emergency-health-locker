import streamlit as st
import requests
from utils.pdf_generator import generate_medical_pdf

st.set_page_config(
    page_title="Emergency Medical Information",
    page_icon="🚑",
    layout="wide"
)

# 🔒 HIDE SIDEBAR
st.markdown("""
<style>
section[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.emergency-header {
    background-color: #ff4444;
    color: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="emergency-header"><h1>🚑 EMERGENCY MEDICAL INFORMATION</h1>'
    '<p>For Emergency Use Only</p></div>',
    unsafe_allow_html=True
)

patient_id = st.query_params.get("patient_id")

if not patient_id:
    st.error("❌ Invalid access. Please scan the QR code.")
    st.stop()

with st.spinner("Loading emergency information..."):
    res = requests.get(
        f"https://emergency-health-locker.onrender.com/api/public/{patient_id}",
        timeout=10
    )

if res.status_code != 200:
    st.error("Unable to load emergency record")
    st.stop()

patient = res.json()

st.success(f"Emergency record loaded for **{patient.get('Name','Unknown')}**")
st.divider()

col1, col2, col3, col4 = st.columns(4)
col1.metric("PATIENT ID", patient.get("Patient_ID", "N/A"))
col2.metric("BLOOD GROUP", patient.get("Blood_Type", "N/A"))
col3.metric("DOB", patient.get("Date_of_Birth", "N/A"))
col4.metric("GENDER", patient.get("Gender", "N/A"))

if patient.get("Emergency_Status"):
    st.error(f"⚠️ {patient['Emergency_Status']}")

st.divider()

st.markdown("### 🚨 Allergies")
st.info(patient.get("Drug_Allergies", "None"))

st.markdown("### 💊 Medications")
st.info(patient.get("Current_Medications", "None"))

st.markdown("### 📞 Emergency Contact")
st.info(patient.get("Emergency_Contacts", "Not available"))

st.divider()

pdf = generate_medical_pdf(patient)
st.download_button(
    "📥 Download Complete Medical PDF",
    pdf,
    file_name=f"Emergency_{patient_id}.pdf",
    mime="application/pdf"
)

st.caption("QURE • Emergency Access")
