import streamlit as st

st.set_page_config(
    page_title="QURE – Emergency Health Locker",
    page_icon="🚑",
    layout="wide"
)

# Minimal welcome (Streamlit requires a root page)
st.title("🚑 QURE – Emergency Health Locker")

st.info(
    "Please use the navigation provided by the app. "
    "Login page will load automatically."
)

# Auto-redirect to Login
st.switch_page("pages/0_Login.py")
