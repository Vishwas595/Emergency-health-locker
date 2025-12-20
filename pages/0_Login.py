import streamlit as st

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Login | QCURE ",
    page_icon="🔐",
    layout="centered"
)

# ===============================
# SESSION INIT
# ===============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None

# ===============================
# AUTO REDIRECT IF LOGGED IN
# ===============================
if st.session_state.logged_in:
    if st.session_state.role == "ADMIN":
        st.switch_page("pages/2_Admin.py")
    else:
        st.switch_page("pages/1_User.py")

# ===============================
# UI STYLING
# ===============================
st.markdown("""
<style>
.login-box {
    max-width: 420px;
    margin: auto;
    padding: 30px;
    border-radius: 12px;
    background-color: #f9f9f9;
    box-shadow: 0px 0px 20px rgba(0,0,0,0.1);
}
.title {
    text-align: center;
    font-size: 28px;
    font-weight: bold;
}
.subtitle {
    text-align: center;
    color: gray;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# LOGIN BOX
# ===============================
st.markdown('<div class="login-box">', unsafe_allow_html=True)

st.markdown('<div class="title">🔐 QCURE</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Secure Login</div>', unsafe_allow_html=True)

with st.form("login_form"):
    name = st.text_input("Full Name")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")

    login_btn = st.form_submit_button("Login / Sign Up")

# ===============================
# LOGIN LOGIC (PHASE 4B – BASIC)
# ===============================
if login_btn:
    if not name or not phone or not email or not password:
        st.error("❌ All fields are required")
    else:
        # 🔐 PREDEFINED ADMIN CREDENTIALS
        ADMIN_EMAIL = "admin@ehlocker.com"
        ADMIN_PHONE = "7397617895"

        st.session_state.logged_in = True
        st.session_state.user_email = email

        if email == ADMIN_EMAIL and phone == ADMIN_PHONE:
            st.session_state.role = "ADMIN"
            st.success("✅ Admin login successful")
            st.switch_page("pages/2_Admin.py")
        else:
            st.session_state.role = "USER"
            st.success("✅ User login successful")
            st.switch_page("pages/1_User.py")

st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# FOOTER
# ===============================
st.markdown(
    "<p style='text-align:center; color:gray;'>Emergency Health Locker © 2025</p>",
    unsafe_allow_html=True
)
