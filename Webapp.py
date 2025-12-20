import streamlit as st

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="QCURE - Emergency Health Locker",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===============================
# CUSTOM CSS - PROFESSIONAL MEDICAL THEME
# ===============================
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Remove padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    
    /* Loading animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.8s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# LANDING LOGIC
# ===============================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("pages/0_Login.py")
else:
    role = st.session_state.get("role")
    
    if role == "ADMIN":
        st.switch_page("pages/2_Admin.py")
    elif role == "USER":
        st.switch_page("pages/1_User.py")
    else:
        st.session_state.clear()
        st.switch_page("pages/0_Login.py")