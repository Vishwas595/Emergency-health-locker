import streamlit as st
import requests
from utils.pdf_generator import generate_medical_pdf

st.set_page_config(
    page_title="Emergency Medical Info | QURE",
    page_icon="🚑",
    layout="wide"
)

# Hide sidebar only
st.markdown("""
<style>
section[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

API_BASE = "https://emergency-health-locker.onrender.com/api"


st.title("🚑 Emergency Medical Information")
st.warning("For emergency use only")

patient_id = st.query_params.get("patient_id")

if not patient_id:
    st.error("Invalid access. Scan QR code.")
    st.stop()

with st.spinner("Loading emergency data..."):
    try:
        res = requests.get(
            f"{API_BASE}/public/{patient_id}",
            timeout=5
        )
    except requests.exceptions.RequestException:
        st.error("Server unavailable")
        st.stop()

if res.status_code != 200:
    st.error("Patient not found")
    st.stop()

patient = res.json()

st.success(f"Patient: {patient.get('Name')}")

st.metric("Blood Group", patient.get("Blood_Type", "N/A"))
st.metric("Emergency Contact", patient.get("Emergency_Contacts", "N/A"))

pdf = generate_medical_pdf(patient)
st.download_button(
    "Download Medical PDF",
    pdf,
    file_name=f"Emergency_{patient_id}.pdf",
    mime="application/pdf"
)
