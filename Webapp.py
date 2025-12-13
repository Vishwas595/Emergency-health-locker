import streamlit as st
import requests
import qrcode
import tempfile
from PIL import Image
from io import BytesIO
from fpdf import FPDF
import os

# Backend API URL (ensure your Node server is running on port 5000)
BASE_URL = "http://localhost:5000/api/patients"

# For generating online QR links (replace with actual deployment if needed)
APP_URL = "http://localhost:8501"

# ---------------------------
# Helper Functions
# ---------------------------

def api_request(method, patient_id=None, data=None):
    """Handles API requests to the Express backend."""
    try:
        if method == "GET":
            url = f"{BASE_URL}/{patient_id}" if patient_id else BASE_URL
            res = requests.get(url)
            if res.status_code == 200:
                return res.json()
            else:
                return None
        elif method == "POST":
            res = requests.post(BASE_URL, json=data)
            return res.json() if res.status_code == 201 else None
    except Exception as e:
        st.error(f"API Error: Could not connect to backend server ({BASE_URL}).")
        st.error(f"Details: {e}")
        return None

def create_smart_qr(patient):
    """Creates a QR code with online URL and offline data."""
    patient_id = patient['Patient_ID']
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
    """Generates the PDF report as bytes."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="EMERGENCY MEDICAL PROFILE", ln=True, align='C')
    pdf.line(10, 20, 200, 20)
    pdf.ln(15)

    pdf.set_font("Arial", size=12)
    details = [
        f"Patient ID: {patient.get('Patient_ID')}",
        f"Name: {patient.get('Name')}",
        f"Blood Type: {patient.get('Blood_Type', 'N/A')}",
        f"Gender: {patient.get('Gender', 'N/A')}",
        f"Emergency Status: {patient.get('Emergency_Status', 'N/A')}"
    ]
    for line in details:
        pdf.cell(200, 10, txt=line, ln=True, align='L')

    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt="Note: QR works offline (text) or online (profile link).", ln=True)

    qr_img = create_smart_qr(patient)
    temp_filename = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            temp_filename = tmp_file.name
            qr_img.save(temp_filename)
        pdf.image(temp_filename, x=150, y=30, w=40)
    except Exception as e:
        st.error(f"Error inserting QR code into PDF: {e}")
    finally:
        if temp_filename and os.path.exists(temp_filename):
            os.remove(temp_filename)

    # FIX: encode to bytes for Streamlit
    return pdf.output(dest='S').encode('latin1')


def show_patient(patient):
    """Displays patient data, QR code, and download button."""
    st.success("Patient Record Found")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Patient Details")
        st.write(f"**Patient ID:** {patient.get('Patient_ID')}")
        st.write(f"**Name:** {patient.get('Name')}")
        st.write(f"**Blood Type:** {patient.get('Blood_Type', 'N/A')}")
        st.write(f"**Gender:** {patient.get('Gender', 'N/A')}")
        st.write(f"**Emergency Status:** {patient.get('Emergency_Status', 'N/A')}")
        
        pdf_bytes = create_pdf(patient)
        st.download_button(
            label="📄 Download Medical Report (PDF)",
            data=pdf_bytes,
            file_name=f"Medical_Report_{patient['Patient_ID']}.pdf",
            mime="application/pdf"
        )
    
    with col2:
        st.write("---")
        qr_img = create_smart_qr(patient)
        buf = BytesIO()
        qr_img.save(buf, format='PNG')
        st.image(buf, caption="Smart Emergency QR Code", use_container_width=True)
        st.caption("ℹ️ Scans offline (text) OR links online (full profile).")

# ---------------------------
# Streamlit App
# ---------------------------

st.set_page_config(page_title="Emergency Health Locker", page_icon="🏥")
st.title("🏥 Emergency Health Locker")

# --- Logic 1: Handle URL Parameters (QR Scan or direct link) ---
patient_id_param = st.query_params.get("patient_id", [None])[0]
if patient_id_param:
    st.info(f"Retrieving records for ID: **{patient_id_param}**")
    patient = api_request("GET", patient_id_param)
    if patient:
        show_patient(patient)
    else:
        st.error("Patient not found.")
    st.divider()

# --- Logic 2: Manual Search ---
st.header("🔍 Retrieve Existing Patient")
col_search_1, col_search_2 = st.columns([3, 1])

with col_search_1:
    search_id = st.text_input("Enter Patient ID to Search", placeholder="e.g., P001")

with col_search_2:
    st.write("")
    st.write("")
    search_btn = st.button("Search Patient", type="primary")

if search_btn and search_id:
    result = api_request("GET", patient_id=search_id)
    if result:
        show_patient(result)
    else:
        st.warning(f"No patient found with ID: {search_id}")

st.divider()

# --- Logic 3: Add New Patient ---
st.header("📝 Add New Patient")
with st.form("add_patient_form"):
    col_a, col_b = st.columns(2)
    with col_a:
        patient_id = st.text_input("Patient ID (Unique)", help="Must be unique.")
        name = st.text_input("Full Name")
        blood_type = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
    with col_b:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        emergency_status = st.text_input("Medical Alert", placeholder="e.g. Diabetic, Severe Penicillin Allergy")
    
    submitted = st.form_submit_button("Save to Database")
    
    if submitted:
        if patient_id and name:
            data = {
                "Patient_ID": patient_id,
                "Name": name,
                "Blood_Type": blood_type,
                "Gender": gender,
                "Emergency_Status": emergency_status
            }
            res = api_request("POST", data=data)
            if res:
                show_patient(res)
            else:
                st.error("Failed to add patient. Patient ID might already exist.")
        else:
            st.warning("Please fill in Patient ID and Name.")
