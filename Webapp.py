import streamlit as st
import requests
import qrcode
import tempfile
from PIL import Image
from io import BytesIO
from fpdf import FPDF
import os

# ===============================
# ✅ PRODUCTION URLs (UPDATED)
# ===============================

BASE_URL = "https://emergency-health-locker.onrender.com/api/patients"
APP_URL = "https://emergency-health-locker-jvaaiwgtsr3u8iwxscdebb.streamlit.app"

# ---------------------------
# Helper Functions
# ---------------------------

def api_request(method, patient_id=None, data=None):
    """Handles API requests to the Express backend."""
    try:
        if method == "GET":
            url = f"{BASE_URL}/{patient_id}" if patient_id else BASE_URL
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                return res.json()
            else:
                return None

        elif method == "POST":
            res = requests.post(BASE_URL, json=data, timeout=10)
            return res.json() if res.status_code in [200, 201] else None

    except Exception as e:
        st.error("❌ Unable to connect to backend server.")
        st.code(str(e))
        return None


def create_smart_qr(patient):
    """Creates a QR code with online URL + offline emergency data."""
    patient_id = patient["Patient_ID"]

    online_url = f"{APP_URL}/?patient_id={patient_id}"

    offline_data = (
        f"Name: {patient['Name']}\n"
        f"ID: {patient['Patient_ID']}\n"
        f"Blood: {patient.get('Blood_Type', 'N/A')}\n"
        f"Gender: {patient.get('Gender', 'N/A')}\n"
        f"Alert: {patient.get('Emergency_Status', 'None')}"
    )

    qr_payload = f"{online_url}|{offline_data}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img


def create_pdf(patient):
    """Generates PDF medical report."""
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "EMERGENCY MEDICAL PROFILE", ln=True, align="C")
    pdf.line(10, 20, 200, 20)
    pdf.ln(15)

    pdf.set_font("Arial", size=12)
    details = [
        f"Patient ID: {patient.get('Patient_ID')}",
        f"Name: {patient.get('Name')}",
        f"Blood Type: {patient.get('Blood_Type', 'N/A')}",
        f"Gender: {patient.get('Gender', 'N/A')}",
        f"Emergency Status: {patient.get('Emergency_Status', 'N/A')}",
    ]

    for line in details:
        pdf.cell(200, 10, line, ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(200, 10, "QR works offline (text) and online (profile link).", ln=True)

    qr_img = create_smart_qr(patient)
    temp_file = ""

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            temp_file = tmp.name
            qr_img.save(temp_file)

        pdf.image(temp_file, x=150, y=30, w=40)

    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)

    return pdf.output(dest="S").encode("latin1")


def show_patient(patient):
    """Display patient info, QR & PDF."""
    st.success("✅ Patient Record Found")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Patient Details")
        st.write(f"**Patient ID:** {patient['Patient_ID']}")
        st.write(f"**Name:** {patient['Name']}")
        st.write(f"**Blood Type:** {patient.get('Blood_Type', 'N/A')}")
        st.write(f"**Gender:** {patient.get('Gender', 'N/A')}")
        st.write(f"**Emergency Status:** {patient.get('Emergency_Status', 'N/A')}")

        pdf_bytes = create_pdf(patient)
        st.download_button(
            "📄 Download Medical Report (PDF)",
            data=pdf_bytes,
            file_name=f"Medical_Report_{patient['Patient_ID']}.pdf",
            mime="application/pdf",
        )

    with col2:
        qr_img = create_smart_qr(patient)
        buf = BytesIO()
        qr_img.save(buf, format="PNG")
        st.image(buf, caption="Smart Emergency QR", use_container_width=True)


# ---------------------------
# Streamlit App UI
# ---------------------------

st.set_page_config(page_title="Emergency Health Locker", page_icon="🏥")
st.title("🏥 Emergency Health Locker")

# ---- QR / URL Scan ----
patient_id_param = st.query_params.get("patient_id")


if patient_id_param:
    st.info(f"Fetching patient ID: **{patient_id_param}**")
    patient = api_request("GET", patient_id_param)
    if patient:
        show_patient(patient)
    else:
        st.error("❌ Patient not found.")
    st.divider()

# ---- Search Patient ----
st.header("🔍 Retrieve Existing Patient")
search_id = st.text_input("Enter Patient ID", placeholder="P001")

if st.button("Search Patient"):
    result = api_request("GET", search_id)
    if result:
        show_patient(result)
    else:
        st.warning("No patient found.")

st.divider()

# ---- Add Patient ----
st.header("📝 Add New Patient")

with st.form("add_patient_form"):
    col1, col2 = st.columns(2)

    with col1:
        patient_id = st.text_input("Patient ID")
        name = st.text_input("Full Name")
        blood_type = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

    with col2:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        emergency_status = st.text_input("Medical Alert")

    submitted = st.form_submit_button("Save Patient")

    if submitted:
        if patient_id and name:
            payload = {
                "Patient_ID": patient_id,
                "Name": name,
                "Blood_Type": blood_type,
                "Gender": gender,
                "Emergency_Status": emergency_status,
            }

            res = api_request("POST", data=payload)
            if res:
                show_patient(res)
            else:
                st.error("❌ Failed to add patient (ID may already exist).")
        else:
            st.warning("Patient ID and Name are required.")
