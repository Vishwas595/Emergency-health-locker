import streamlit as st
import requests

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Admin Panel | QCURE",
    page_icon="🛠️",
    layout="wide"
)

# ===============================
# ADMIN SECRET (SAFE LOAD)
# ===============================
if "ADMIN_SECRET" in st.secrets:
    ADMIN_SECRET = st.secrets["ADMIN_SECRET"]
else:
    ADMIN_SECRET = "admin123"  # local fallback only

HEADERS = {
    "x-admin-key": ADMIN_SECRET
}

# ===============================
# SESSION AUTH CHECK
# ===============================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("❌ Please login first")
    st.stop()

if st.session_state.get("role") != "ADMIN":
    st.error("❌ Unauthorized access")
    st.stop()

# ===============================
# BACKEND URL
# ===============================
BACKEND_URL = "https://emergency-health-locker.onrender.com/api/patients"

# ===============================
# HEADER
# ===============================
st.title("🛠️ Admin Panel")
st.markdown("### Manage Patient Records")

# Logout
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.switch_page("pages/0_Login.py")

st.divider()

# ===============================
# TABS
# ===============================
tab1, tab2, tab3 = st.tabs(
    ["➕ Add Patient", "📋 View Patients", "ℹ️ System Info"]
)

# =====================================================
# TAB 1: ADD PATIENT
# =====================================================
with tab1:
    st.subheader("➕ Add New Patient")

    with st.form("add_patient_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            patient_id = st.text_input("Patient ID *", placeholder="P001")
            name = st.text_input("Full Name *")

        with col2:
            dob = st.date_input("Date of Birth")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])

        with col3:
            blood = st.selectbox(
                "Blood Group",
                ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            )
            emergency_contact = st.text_input("Emergency Contact")

        st.divider()

        col4, col5 = st.columns(2)
        with col4:
            medications = st.text_area("Current Medications")
            drug_allergies = st.text_area("Drug Allergies")

        with col5:
            other_allergies = st.text_area("Other Allergies")
            surgeries = st.text_area("Recent Surgeries")

        st.divider()

        col6, col7 = st.columns(2)
        with col6:
            vital_signs = st.text_input("Last Vital Signs")
            devices = st.text_input("Medical Devices")

        with col7:
            dnr = st.checkbox("DNR (Do Not Resuscitate)")
            donor = st.checkbox("Organ Donor")

        emergency_status = st.text_area("Emergency Alert / Condition")

        submit = st.form_submit_button("💾 Save Patient")

        if submit:
            if not patient_id or not name:
                st.error("❌ Patient ID and Name are required")
            else:
                payload = {
                    "Patient_ID": patient_id,
                    "Name": name,
                    "Date_of_Birth": str(dob),
                    "Gender": gender,
                    "Blood_Type": blood,
                    "Emergency_Contacts": emergency_contact,
                    "Emergency_Status": emergency_status,
                    "Current_Medications": medications or "None",
                    "Drug_Allergies": drug_allergies or "None",
                    "Other_Allergies": other_allergies or "None",
                    "Recent_Surgeries": surgeries or "None",
                    "Vital_Signs_Last_Recorded": vital_signs,
                    "Medical_Devices": devices or "None",
                    "DNR_Status": dnr,
                    "Organ_Donor": donor
                }

                res = requests.post(
                    BACKEND_URL,
                    json=payload,
                    headers=HEADERS,
                    timeout=10
                )

                if res.status_code in [200, 201]:
                    st.success("✅ Patient added successfully")
                else:
                    st.error(res.text)

# =====================================================
# TAB 2: VIEW PATIENTS (FIXED 🔥)
# =====================================================
with tab2:
    st.subheader("📋 Registered Patients")

    if st.button("🔄 Refresh"):
        st.rerun()

    res = requests.get(BACKEND_URL, headers=HEADERS, timeout=10)

    if res.status_code == 200:
        patients = res.json().get("patients", [])

        if not patients:
            st.info("No patients found")
        else:
            st.success(f"Total Patients: {len(patients)}")

            search = st.text_input("🔍 Search by ID or Name")

            # ✅ SAFE SEARCH (NO KeyError)
            if search:
                search = search.lower()
                patients = [
                    p for p in patients
                    if search in (p.get("Patient_ID", "") or "").lower()
                    or search in (p.get("Name", "") or "").lower()
                ]

            for p in patients:
                with st.container(border=True):
                    st.markdown(f"**{p.get('Name', 'Unknown')}**")
                    st.caption(f"ID: {p.get('Patient_ID', 'N/A')}")
                    st.text(f"Blood: {p.get('Blood_Type', '-')}")
                    st.text(f"Gender: {p.get('Gender', '-')}")
                    if p.get("Emergency_Status"):
                        st.warning(p["Emergency_Status"])
    else:
        st.error("❌ Failed to load patients (Admin key missing or backend down)")

# =====================================================
# TAB 3: SYSTEM INFO
# =====================================================
with tab3:
    st.subheader("ℹ️ System Information")

    st.info("""
    **Backend**
    - Node.js + Express
    - MongoDB Atlas
    - Hosted on Render

    **Frontend**
    - Streamlit Cloud
    - Role-based access
    - QR + NFC support
    """)

    if st.button("🔧 Test Backend"):
        try:
            test = requests.get(
                "https://emergency-health-locker.onrender.com",
                timeout=5
            )
            if test.status_code == 200:
                st.success("✅ Backend is live")
            else:
                st.error("❌ Backend issue")
        except:
            st.error("❌ Backend unreachable")

st.divider()
st.caption("QCURE • Admin Module • Phase 4B ✅ COMPLETE")
