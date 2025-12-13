import streamlit as st
import hashlib

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_admin_password():
    """Check if admin is logged in, return True if yes"""
    
    # Initialize session state
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    
    # If already logged in, return True
    if st.session_state.admin_logged_in:
        return True
    
    # Show login form
    st.title("🔐 Admin Login Required")
    st.warning("This page is restricted to authorized administrators only.")
    
    with st.form("admin_login_form"):
        password = st.text_input("Enter Admin Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            # Change this password in production!
            # Current password: admin123
            correct_hash = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
            
            if hash_password(password) == correct_hash:
                st.session_state.admin_logged_in = True
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Incorrect password")
    
    st.divider()
    st.caption("Default password: admin123 (Change in production)")
    
    return False

def logout_admin():
    """Logout admin"""
    if st.button("🚪 Logout"):
        st.session_state.admin_logged_in = False
        st.rerun()