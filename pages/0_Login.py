import streamlit as st
import requests
import base64

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Login | QURE",
    page_icon="🔐",
    layout="centered"
)

# ===============================
# GLOBAL CSS FIXES (REMOVE WHITE BOX)
# ===============================
st.markdown("""
<style>

/* ---- FULL RESET OF STREAMLIT LAYOUT ---- */

/* Remove ALL top spacing */
section.main > div {
    padding-top: 0rem !important;
}

/* Remove first empty block */
section.main > div > div:first-child {
    display: none !important;
}

/* Remove Streamlit header completely */
header {
    display: none !important;
}

/* Remove white background from root */
div[data-testid="stAppViewContainer"] {
    background-color: #0e1117 !important;
}

/* Remove any leftover rounded containers */
div[data-testid="stVerticalBlock"] {
    background: transparent !important;
    box-shadow: none !important;
}

/* Hide sidebar */
section[data-testid="stSidebar"] {
    display: none !important;
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
# LOAD LOGO (BASE64 SAFE)
# ===============================
with open("assets/qure_logo.png", "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

# ===============================
# UI STYLING
# ===============================
st.markdown("""
<style>
.login-box {
    max-width: 460px;
    margin: 60px auto;
    padding: 34px;
    border-radius: 18px;
    background: #f9f9f9;
    box-shadow: 0 12px 35px rgba(0,0,0,0.18);
}

.logo {
    width: 130px;
    margin-bottom: 12px;
}

.title {
    text-align: center;
    font-size: 30px;
    font-weight: 700;
    margin-top: 6px;
    color: #111827;
}

.subtitle {
    text-align: center;
    color: #6b7280;
    margin-bottom: 26px;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# LOGIN CONTAINER
# ===============================
st.markdown('<div class="login-box">', unsafe_allow_html=True)

st.markdown(f"""
<div style="text-align:center;">
    <img class="logo" src="data:image/png;base64,{logo_base64}">
    <div class="title">🔐 QURE</div>
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

# ==================================================
# 📝 REGISTER (PATIENT ONLY)
# ==================================================
if mode == "📝 Register":
    st.subheader("📝 Register")

    name = st.text_input("Full Name *")
    patient_id = st.text_input("Patient ID *", placeholder="e.g., P005")
    phone = st.text_input("Phone Number *", placeholder="10-digit mobile number")

    if st.button("Register"):
        if not name or not patient_id or not phone:
            st.error("❌ All fields are required")
        elif patient_id == ADMIN_ID:
            st.error("❌ Admin cannot be registered")
        else:
            res = requests.get(f"{API_BASE}/patients/{patient_id}")

            if res.status_code == 200:
                st.error("❌ Patient already exists. Please Sign In.")
            else:
                payload = {
                    "Patient_ID": patient_id,
                    "Name": name,
                    "Phone_Number": phone
                }

                create = requests.post(
                    f"{API_BASE}/user/patients",
                    json=payload,
                    timeout=15
                )

                if create.status_code in [200, 201]:
                    st.success("✅ Registration successful. Please Sign In.")
                else:
                    st.error("❌ Registration failed")

# ==================================================
# 🔑 SIGN IN (AUTO ROLE)
# ==================================================
if mode == "🔑 Sign In":
    st.subheader("🔑 Sign In")

    entered_id = st.text_input("ID")
    phone = st.text_input("Phone Number")

    if st.button("Sign In"):
        if not entered_id or not phone:
            st.error("❌ Both fields are required")
            st.stop()

        # ADMIN LOGIN
        if entered_id == ADMIN_ID:
            if phone == ADMIN_PHONE:
                st.session_state.logged_in = True
                st.session_state.role = "ADMIN"
                st.success("✅ Admin login successful")
                st.switch_page("pages/2_Admin.py")
            else:
                st.error("❌ Invalid admin credentials")

        # USER LOGIN
        else:
            res = requests.get(f"{API_BASE}/patients/{entered_id}")

            if res.status_code != 200:
                st.error("❌ Invalid Patient ID")
            else:
                patient = res.json()
                db_phone = str(patient.get("Phone_Number", ""))

                if db_phone != phone:
                    st.error("❌ Incorrect phone number")
                else:
                    st.session_state.logged_in = True
                    st.session_state.role = "USER"
                    st.session_state.patient_id = entered_id
                    st.success("✅ Login successful")
                    st.switch_page("pages/1_User.py")

st.markdown("</div>", unsafe_allow_html=True)
st.caption("QURE © 2025")
