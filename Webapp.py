import streamlit as st
import requests

st.set_page_config(
    page_title="Emergency Health Locker",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Emergency Health Locker")
st.markdown("### Instant Access to Medical Information in Emergencies")

st.divider()

# Three cards explaining each section
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 👤 For Patients")
    st.info("""
    **User Dashboard**
    
    - View your medical details
    - Generate QR code
    - Copy link for NFC card
    - Download medical PDF
    
    👉 Go to **👤 User** page in sidebar
    """)

with col2:
    st.markdown("### 🛠️ For Administrators")
    st.warning("""
    **Admin Panel**
    
    - Add new patients
    - Update medical records
    - Manage patient data
    - View all 251+ patients
    
    🔐 Password protected
    
    👉 Go to **🛠️ Admin** page
    """)

with col3:
    st.markdown("### 🚑 For Emergency")
    st.error("""
    **Emergency Access**
    
    - Scan QR code
    - View critical info only
    - Access emergency details
    - Download medical history
    
    ⚡ Instant access via QR/NFC
    """)

st.divider()

st.markdown("### 🔍 Quick Navigation")
st.markdown("""
Use the **sidebar** (← left) to navigate to different sections:

- **👤 User** - For patients to view their info and get QR codes
- **🛠️ Admin** - For administrators to manage records (password: admin123)
- **🚑 Public** - Emergency page (opened by QR code scan)
""")

# Backend status check
BACKEND_URL = "https://emergency-health-locker.onrender.com"

st.divider()

with st.expander("🔧 System Status & Info"):
    col_status1, col_status2 = st.columns(2)
    
    with col_status1:
        st.markdown("**Backend Server**")
        try:
            response = requests.get(BACKEND_URL, timeout=5)
            if response.status_code == 200:
                st.success("✅ Online")
            else:
                st.warning("⚠️ Unusual response")
        except:
            st.error("❌ Offline (may be spinning up)")
            st.caption("Free tier spins down after inactivity. First request may take 30-50 seconds.")
    
    with col_status2:
        st.markdown("**Database**")
        try:
            response = requests.get(f"{BACKEND_URL}/api/patients", timeout=10)
            if response.status_code == 200:
                patients = response.json()
                if isinstance(patients, list):
                    st.success(f"✅ Connected ({len(patients)} patients)")
                elif isinstance(patients, dict) and 'patients' in patients:
                    st.success(f"✅ Connected ({len(patients['patients'])} patients)")
                else:
                    st.success("✅ Connected")
            else:
                st.warning("⚠️ Connection issue")
        except:
            st.error("❌ Cannot reach database")

st.divider()

st.markdown("### 📱 How It Works")
col_how1, col_how2, col_how3 = st.columns(3)

with col_how1:
    st.markdown("**1️⃣ Register**")
    st.write("Admin adds patient details to the system with complete medical history.")

with col_how2:
    st.markdown("**2️⃣ Generate QR**")
    st.write("Patient gets QR code and NFC link from their dashboard.")

with col_how3:
    st.markdown("**3️⃣ Emergency Use**")
    st.write("Emergency personnel scan QR/NFC to access critical medical info instantly.")

st.divider()

st.caption("Emergency Health Locker v1.0 | Powered by NFC & QR Technology")
st.caption("Backend: Render + MongoDB Atlas | Frontend: Streamlit Cloud")