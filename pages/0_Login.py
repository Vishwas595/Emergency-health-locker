import streamlit as st
import requests
import base64

# ===============================
# PAGE CONFIG (IMPORTANT)
# ===============================
st.set_page_config(
    page_title="Login | QURE",
    page_icon="🔐",
    layout="wide"   # ✅ MUST be wide (prevents white spacer)
)

# ===============================
# GLOBAL CSS (CLEAN + STABLE)
# ===============================
st.markdown("""
<style>

/* Hide Streamlit header & sidebar */
header, footer, section[data-testid="stSidebar"] {
    display: none !important;
}

/* Remove top padding */
.block-container {
    padding-top: 0 !important;
}

/* App background */
div[data-testid="stAppViewContainer"] {
    background-color: #0e1117;
}

/* Center wrapper */
.login-wrapper {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* Login card */
.login-box {
    width: 460px;
    padding: 36px;
    border-radius: 18px;
    background: #f9f9f9;
    box-shadow: 0 14px 40px rgba(0,0,0,0.25);
}

/* Logo */
.logo {
    width: 140px;
    margin-bottom: 14px;
}

/* Text */
.title {
    font-size: 30px;
    font-weight: 700;
    text-align: center;
    color: #111827;
}

.subtitle {
    text-align: center;
    color: #6b7280;
    margin-bottom: 28px;
}

</style>
""", unsafe_allow_html=True)

API_BASE = "http://localhost:5000/api"

# ===============================
# ADMIN CREDENTIALS
# ===============================
ADMIN_ID = st.secrets.get("ADMIN_ID", "ADMIN001")
ADMIN_PHONE = st.secrets.get("ADMIN_PHONE", "7397617895")

# ===============================
# SESSION INIT
# ===============================
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("role", None)
st.session_state.setdefault("patient_id", None)

# ===============================
# AUTO REDIRECT
# ===============================
if st.session_state.logged_in:
    if st.session_state.role == "ADMIN":
        st.switch_page("pages/2_Admin.py")
    else:
        st.switch_page("pages/1_User.py")

# ===============================
# LOAD LOGO
# ===============================
with open("assets/qure_logo.png", "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

# ===============================
# UI START
# ===============================
st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
st.markdown('<div class="login-box">', unsafe_allow_html=True)

# Logo replaces white box area
st.markdown(f"""
<div style="text-align:center;">
    <img src="data:image/png;base64,{logo_base64}" class="logo">
    <div class="title">QURE</div>
    <div class="subtitle">Secure Medical Access</div>
</div>
""", unsafe_allow_html=True)

# ===============================
# MODE SELECT
# ===============================
mode = st.radio(
    "Choose an option",
    ["🔑 Sign In", "📝 Register"],
    horizontal=True
)

# ===============================
# REGISTER
# ===============================
if mode == "📝 Register":
    st.subheader("📝 Register")

    name = st.text_input("Full Name *")
    patient_id = st.text_input("Patient ID *")
    phone = st.text_input("Phone Number *")

    if st.button("Register"):
        if not name or not patient_id or not phone:
            st.error("❌ All fields are required")
        elif patient_id == ADMIN_ID:
            st.error("❌ Admin cannot be registered")
        else:
            check = requests.get(f"{API_BASE}/patients/{patient_id}")
            if check.status_code == 200:
                st.error("❌ Patient already exists. Please Sign In.")
            else:
                payload = {
                    "Patient_ID": patient_id,
                    "Name": name,
                    "Phone_Number": phone
                }
                res = requests.post(f"{API_BASE}/user/patients", json=payload)
                if res.status_code in [200, 201]:
                    st.success("✅ Registration successful. Please Sign In.")
                else:
                    st.error("❌ Registration failed")

# ===============================
# SIGN IN
# ===============================
if mode == "🔑 Sign In":
    st.subheader("🔑 Sign In")

    entered_id = st.text_input("ID")
    phone = st.text_input("Phone Number")

    if st.button("Sign In"):
        if not entered_id or not phone:
            st.error("❌ Both fields are required")
            st.stop()

        # ADMIN
        if entered_id == ADMIN_ID and phone == ADMIN_PHONE:
            st.session_state.logged_in = True
            st.session_state.role = "ADMIN"
            st.switch_page("pages/2_Admin.py")

        # USER
        else:
            res = requests.get(f"{API_BASE}/patients/{entered_id}")
            if res.status_code != 200:
                st.error("❌ Invalid ID")
            elif str(res.json().get("Phone_Number")) != phone:
                st.error("❌ Incorrect phone number")
            else:
                st.session_state.logged_in = True
                st.session_state.role = "USER"
                st.session_state.patient_id = entered_id
                st.switch_page("pages/1_User.py")

st.markdown("</div></div>", unsafe_allow_html=True)
st.caption("QURE © 2025")
