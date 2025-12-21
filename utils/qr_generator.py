import streamlit as st
import requests
import base64
import os

# ===============================
# PAGE CONFIG (MUST BE FIRST)
# ===============================
st.set_page_config(
    page_title="Login | QURE",
    page_icon="🔒",
    layout="wide"
)

# ===============================
# SESSION INIT (BEFORE EVERYTHING)
# ===============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "patient_id" not in st.session_state:
    st.session_state.patient_id = None

# ===============================
# CONSTANTS
# ===============================
API_BASE = "https://emergency-health-locker.onrender.com/api"

try:
    ADMIN_ID = st.secrets.get("ADMIN_ID", "ADMIN001")
    ADMIN_PHONE = st.secrets.get("ADMIN_PHONE", "7397617895")
except:
    ADMIN_ID = "ADMIN001"
    ADMIN_PHONE = "7397617895"

# ===============================
# AUTO REDIRECT (AFTER SESSION INIT)
# ===============================
if st.session_state.logged_in:
    if st.session_state.role == "ADMIN":
        st.switch_page("pages/2_Admin.py")
    else:
        st.switch_page("pages/1_User.py")

# ===============================
# LOAD LOGO SAFELY
# ===============================
logo_base64 = ""
logo_path = "assets/qure_logo.png"

if os.path.exists(logo_path):
    try:
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
    except Exception as e:
        st.warning(f"⚠️ Could not load logo: {e}")
else:
    st.warning(f"⚠️ Logo not found at: {logo_path}")

# ===============================
# GLOBAL CSS
# ===============================
st.markdown("""
<style>
/* Hide Streamlit elements */
header, footer, section[data-testid="stSidebar"] {
    display: none !important;
}

/* Remove padding */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
}

/* Dark background */
div[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
}

/* Main wrapper */
.main-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 90vh;
    padding: 20px;
}

/* Login card */
.login-card {
    width: 100%;
    max-width: 440px;
    padding: 40px;
    border-radius: 16px;
    background: rgba(30, 41, 59, 0.95);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(71, 85, 105, 0.3);
}

/* Logo container */
.logo-container {
    text-align: center;
    margin-bottom: 30px;
}

.logo-img {
    width: 120px;
    height: auto;
    margin-bottom: 16px;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
}

/* Title */
.app-title {
    font-size: 36px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 8px;
    letter-spacing: 2px;
}

/* Subtitle */
.app-subtitle {
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 20px;
}

/* Form styling */
label {
    color: #e2e8f0 !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}

input {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 1px solid #475569 !important;
    border-radius: 8px !important;
}

input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
}

/* Radio buttons */
.stRadio > div {
    gap: 12px;
}

.stRadio label {
    background-color: #1e293b;
    padding: 10px 20px;
    border-radius: 8px;
    border: 1px solid #475569;
    transition: all 0.2s;
}

/* Buttons */
button[kind="primary"] {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    transition: all 0.3s !important;
}

button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3) !important;
}

/* Footer */
.footer-text {
    text-align: center;
    color: #64748b;
    font-size: 13px;
    margin-top: 30px;
}

/* Error/Success messages */
.stAlert {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# UI START
# ===============================
st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)
st.markdown('<div class="login-card">', unsafe_allow_html=True)

# Logo and header
st.markdown('<div class="logo-container">', unsafe_allow_html=True)

if logo_base64:
    st.markdown(
        f'<img src="data:image/png;base64,{logo_base64}" class="logo-img">',
        unsafe_allow_html=True
    )

st.markdown('''
<div class="app-title">QURE</div>
<div class="app-subtitle">Secure Medical Access System</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# MODE SELECTOR
# ===============================
mode = st.radio(
    "Choose an option",
    ["🔒 Sign In", "📝 Register"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

# ===============================
# REGISTER MODE
# ===============================
if mode == "📝 Register":
    st.markdown("### 📝 Create Account")
    
    with st.form("register_form", clear_on_submit=False):
        name = st.text_input("Full Name", placeholder="Enter your full name")
        patient_id = st.text_input("Patient ID", placeholder="Your unique patient ID")
        phone = st.text_input("Phone Number", placeholder="10-digit phone number")
        
        submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
        
        if submit:
            if not name or not patient_id or not phone:
                st.error("❌ All fields are required")
            elif patient_id == ADMIN_ID:
                st.error("❌ This ID is reserved for admin use")
            else:
                try:
                    # Check if patient exists
                    check = requests.get(f"{API_BASE}/patients/{patient_id}", timeout=10)
                    
                    if check.status_code == 200:
                        st.error("❌ Patient ID already registered. Please sign in.")
                    else:
                        # Register new patient
                        payload = {
                            "Patient_ID": patient_id,
                            "Name": name,
                            "Phone_Number": phone
                        }
                        
                        res = requests.post(
                            f"{API_BASE}/user/patients",
                            json=payload,
                            timeout=15
                        )
                        
                        if res.status_code in [200, 201]:
                            st.success("✅ Registration successful! Please sign in.")
                        else:
                            st.error(f"❌ Registration failed: {res.text}")
                            
                except requests.exceptions.Timeout:
                    st.error("❌ Server timeout. Please try again.")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to server. Please check your internet.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ===============================
# SIGN IN MODE
# ===============================
elif mode == "🔒 Sign In":
    st.markdown("### 🔒 Sign In")
    
    with st.form("signin_form", clear_on_submit=False):
        entered_id = st.text_input("ID", placeholder="Your Patient ID or Admin ID")
        phone = st.text_input("Phone Number", placeholder="Registered phone number")
        
        submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
        
        if submit:
            if not entered_id or not phone:
                st.error("❌ Both fields are required")
            else:
                # Check for ADMIN
                if entered_id == ADMIN_ID and phone == ADMIN_PHONE:
                    st.session_state.logged_in = True
                    st.session_state.role = "ADMIN"
                    st.success("✅ Admin login successful!")
                    st.rerun()
                
                # Check for USER
                else:
                    try:
                        res = requests.get(f"{API_BASE}/patients/{entered_id}", timeout=10)
                        
                        if res.status_code != 200:
                            st.error("❌ Invalid Patient ID")
                        else:
                            patient_data = res.json()
                            stored_phone = str(patient_data.get("Phone_Number", ""))
                            
                            if stored_phone != phone:
                                st.error("❌ Incorrect phone number")
                            else:
                                st.session_state.logged_in = True
                                st.session_state.role = "USER"
                                st.session_state.patient_id = entered_id
                                st.success("✅ Login successful!")
                                st.rerun()
                                
                    except requests.exceptions.Timeout:
                        st.error("❌ Server timeout. Please try again.")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to server. Please check your internet.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

st.markdown("</div>", unsafe_allow_html=True)  # Close login-card
st.markdown("</div>", unsafe_allow_html=True)  # Close main-wrapper

# Footer
st.markdown(
    '<div class="footer-text">QURE © 2025 • Emergency Health Locker</div>',
    unsafe_allow_html=True
)