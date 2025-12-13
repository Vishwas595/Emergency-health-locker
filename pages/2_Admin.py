import streamlit as st
import requests
from utils.auth import check_admin_password, logout_admin

st.set_page_config(
    page_title="Admin Panel",
    page_icon="🛠️",
    layout="wide"
)

# Check authentication first
if not check_admin_password():
    st.stop()

# If logged in, show admin panel
BACKEND_URL = "https://emergency-health-locker.onrender.com/api/patients"

st.title("🛠️ Admin Panel")
st.markdown("### Manage Patient Records")

# Logout button in top right
col1, col2 = st.columns([6, 1])
with col2:
    logout_admin()

st.divider()

# Tabs for different admin functions
tab1, tab2, tab3 = st.tabs(["➕ Add Patient", "📋 View Patients", "ℹ️ System Info"])

# TAB 1: Add New Patient
with tab1:
    st.markdown("### Add New Patient")
    
    with st.form("add_patient_form", clear_on_submit=True):
        st.markdown("**Basic Information**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            patient_id = st.text_input(
                "Patient ID*",
                placeholder="P001",
                help="Unique identifier (e.g., P001, P002)"
            )
            name = st.text_input(
                "Full Name*",
                placeholder="John Doe"
            )
            dob = st.date_input(
                "Date of Birth",
                help="Patient's date of birth"
            )
        
        with col2:
            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"]
            )
            blood_type = st.selectbox(
                "Blood Type",
                ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            )
            emergency_contact = st.text_input(
                "Emergency Contact",
                placeholder="Phone number"
            )
        
        with col3:
            emergency_status = st.text_area(
                "Emergency Status/Alert",
                placeholder="e.g., Diabetic, Severe allergy to penicillin",
                height=100
            )
        
        st.divider()
        st.markdown("**Medical Information**")
        
        col4, col5 = st.columns(2)
        
        with col4:
            medications = st.text_area(
                "Current Medications",
                placeholder="List medications with dosage"
            )
            drug_allergies = st.text_area(
                "Drug Allergies",
                placeholder="List any drug allergies"
            )
        
        with col5:
            other_allergies = st.text_area(
                "Other Allergies",
                placeholder="Food, environmental allergies"
            )
            surgeries = st.text_area(
                "Recent Surgeries",
                placeholder="List surgeries with dates"
            )
        
        st.divider()
        
        col6, col7 = st.columns(2)
        
        with col6:
            vital_signs = st.text_input(
                "Last Vital Signs",
                placeholder="BP: 120/80, Pulse: 72, Temp: 98.6"
            )
            medical_devices = st.text_input(
                "Medical Devices",
                placeholder="Pacemaker, Insulin pump, etc."
            )
        
        with col7:
            dnr_status = st.checkbox("DNR (Do Not Resuscitate)")
            organ_donor = st.checkbox("Organ Donor")
        
        st.divider()
        
        # Submit button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
        
        with col_btn1:
            submitted = st.form_submit_button("💾 Save Patient", type="primary", use_container_width=True)
        
        with col_btn2:
            st.form_submit_button("🔄 Clear Form", use_container_width=True)
        
        if submitted:
            if not patient_id or not name:
                st.error("❌ Patient ID and Name are required!")
            else:
                # Prepare data
                patient_data = {
                    "Patient_ID": patient_id,
                    "Name": name,
                    "Date_of_Birth": str(dob) if dob else "",
                    "Gender": gender,
                    "Blood_Type": blood_type,
                    "Emergency_Contacts": emergency_contact,
                    "Emergency_Status": emergency_status,
                    "Current_Medications": medications or "None",
                    "Drug_Allergies": drug_allergies or "None",
                    "Other_Allergies": other_allergies or "None",
                    "Recent_Surgeries": surgeries or "None",
                    "Vital_Signs_Last_Recorded": vital_signs,
                    "Medical_Devices": medical_devices or "None",
                    "DNR_Status": dnr_status,
                    "Organ_Donor": organ_donor
                }
                
                # Send to backend
                try:
                    with st.spinner("Saving patient..."):
                        response = requests.post(BACKEND_URL, json=patient_data, timeout=10)
                        
                        if response.status_code == 201:
                            st.success(f"✅ Patient {patient_id} added successfully!")
                            st.balloons()
                        elif response.status_code == 400:
                            st.error("❌ Patient ID already exists. Please use a different ID.")
                        else:
                            st.error(f"⚠️ Error: {response.status_code}")
                
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")

# TAB 2: View All Patients
with tab2:
    st.markdown("### Registered Patients")
    
    if st.button("🔄 Refresh List"):
        st.rerun()
    
    try:
        with st.spinner("Loading patients..."):
            response = requests.get(BACKEND_URL, timeout=10)
            
            if response.status_code == 200:
                patients = response.json()
                
                if isinstance(patients, dict) and 'patients' in patients:
                    patients = patients['patients']
                
                if patients:
                    st.success(f"📊 Total Patients: {len(patients)}")
                    
                    # Search filter
                    search = st.text_input("🔍 Search by ID or Name", "")
                    
                    if search:
                        patients = [
                            p for p in patients 
                            if search.lower() in p.get('Patient_ID', '').lower() 
                            or search.lower() in p.get('Name', '').lower()
                        ]
                    
                    # Display as cards
                    for i in range(0, len(patients), 3):
                        cols = st.columns(3)
                        
                        for j in range(3):
                            if i + j < len(patients):
                                patient = patients[i + j]
                                
                                with cols[j]:
                                    with st.container(border=True):
                                        st.markdown(f"**{patient.get('Name', 'N/A')}**")
                                        st.caption(f"ID: {patient.get('Patient_ID', 'N/A')}")
                                        st.text(f"Blood: {patient.get('Blood_Type', 'N/A')}")
                                        st.text(f"Gender: {patient.get('Gender', 'N/A')}")
                                        
                                        if patient.get('Emergency_Status'):
                                            st.warning(f"⚠️ {patient['Emergency_Status'][:50]}...")
                else:
                    st.info("No patients registered yet.")
            else:
                st.error(f"Failed to load patients: {response.status_code}")
    
    except Exception as e:
        st.error(f"❌ Error loading patients: {str(e)}")

# TAB 3: System Info
with tab3:
    st.markdown("### System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Backend Status**
        
        - API: Render Cloud
        - Database: MongoDB Atlas
        - Status: ✅ Online
        """)
        
        # Test backend
        if st.button("🔧 Test Backend Connection"):
            try:
                response = requests.get("https://emergency-health-locker.onrender.com", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Backend is responsive")
                else:
                    st.warning(f"⚠️ Backend returned: {response.status_code}")
            except:
                st.error("❌ Backend not responding")
    
    with col2:
        st.info("""
        **Frontend Status**
        
        - Platform: Streamlit Cloud
        - Pages: 4 (Home, User, Admin, Public)
        - Status: ✅ Online
        """)
        
        st.markdown("""
        **Features**
        - ✅ Multi-page structure
        - ✅ Admin authentication
        - ✅ QR code generation
        - ✅ NFC support
        - ✅ PDF generation
        """)
    
    st.divider()
    
    st.warning("""
    **⚠️ Security Notes**
    
    - Default admin password is `admin123`
    - Change this in production!
    - Edit `utils/auth.py` to update
    """)

st.divider()
st.caption("Emergency Health Locker Admin Panel v1.0")