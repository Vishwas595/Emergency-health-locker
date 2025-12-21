import streamlit as st
import requests

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Login | QURE",
    page_icon="🔐",
    layout="centered"
)

# Hide sidebar ONLY (safe)
st.markdown("""
<style>
section[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

API_BASE = "https://emergency-health-locker.onrender.com/api"
 # use Render URL when deployed

ADMIN_ID = "ADMIN001"
ADMIN_PHONE = "7397617895"

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
# UI
# ===============================
st.title("🔐 QURE")
st.caption("Secure Medical Access")

mode = st.radio(
    "Choose an option",
    ["🔑 Sign In", "📝 Register"],
    horizontal=True
)

# ===============================
# REGISTER
# ===============================
if mode == "📝 Register":
    name = st.text_input("Full Name")
    patient_id = st.text_input("Patient ID")
    phone = st.text_input("Phone Number")

    if st.button("Register"):
        if not name or not patient_id or not phone:
            st.error("All fields are required")
        else:
            try:
                res = requests.post(
                    f"{API_BASE}/user/patients",
                    json={
                        "Patient_ID": patient_id,
                        "Name": name,
                        "Phone_Number": phone
                    },
                    timeout=5
                )
                if res.status_code in [200, 201]:
                    st.success("Registered successfully. Please sign in.")
                else:
                    st.error("Registration failed")
            except requests.exceptions.RequestException:
                st.error("Backend not reachable")

# ===============================
# SIGN IN
# ===============================
if mode == "🔑 Sign In":
    entered_id = st.text_input("ID")
    phone = st.text_input("Phone Number")

    if st.button("Sign In"):
        if not entered_id or not phone:
            st.error("Both fields required")
            st.stop()

        # ADMIN
        if entered_id == ADMIN_ID and phone == ADMIN_PHONE:
            st.session_state.logged_in = True
            st.session_state.role = "ADMIN"
            st.switch_page("pages/2_Admin.py")

        # USER
        else:
            try:
                res = requests.get(
                    f"{API_BASE}/patients/{entered_id}",
                    timeout=5
                )
                if res.status_code != 200:
                    st.error("Invalid ID")
                elif str(res.json().get("Phone_Number")) != phone:
                    st.error("Incorrect phone number")
                else:
                    st.session_state.logged_in = True
                    st.session_state.role = "USER"
                    st.session_state.patient_id = entered_id
                    st.switch_page("pages/1_User.py")
            except requests.exceptions.RequestException:
                st.error("Backend not reachable")

st.caption("QURE © 2025")
