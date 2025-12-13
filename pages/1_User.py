import streamlit as st
import requests
from utils.qr_generator import generate_emergency_qr, get_public_link, get_nfc_instructions
from utils.pdf_generator import generate_medical_pdf

st.set_page_config(
    page_title="User Dashboard",
    page_icon="👤",
    layout="wide"
)

BACKEND_URL = "https://emergency-health-locker.onrender.com/api/patients"

st.title("👤 User Dashboard")
st.markdown("### View Your Medical Information")

st.divider()

# Patient ID Input
col1, col2 = st.columns([3, 1])

with col1:
    patient_id = st.text_input(
        "Enter Your Patient ID",
        placeholder="e.g., P001",
        help="Your unique patient identifier"
    )

with col2:
    st.write("")
    st.write("")
    search_btn = st.button("🔍 Get My Info", type="primary", use_container_width=True)

if search_btn and patient_id:
    with st.spinner("Fetching your information..."):
        try:
            response = requests.get(f"{BACKEND_URL}/{patient_id}", timeout=10)
            
            if response.status_code == 200:
                patient = response.json()
                
                st.success("✅ Your information loaded successfully!")
                
                st.divider()
                
                # Main content area
                tab1, tab2, tab3 = st.tabs(["📋 My Details", "🔳 QR Code & NFC", "📄 Download PDF"])
                
                # TAB 1: Personal Details
                with tab1:
                    st.markdown("### Your Personal Information")
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown("**Basic Information**")
                        st.info(f"""
                        **Patient ID:** {patient.get('Patient_ID', 'N/A')}  
                        **Name:** {patient.get('Name', 'N/A')}  
                        **Date of Birth:** {patient.get('Date_of_Birth', 'N/A')}  
                        **Gender:** {patient.get('Gender', 'N/A')}  
                        **Blood Type:** {patient.get('Blood_Type', 'N/A')}
                        """)
                        
                        st.markdown("**Emergency Contact**")
                        st.warning(f"📞 {patient.get('Emergency_Contacts', 'Not set')}")
                    
                    with col_b:
                        st.markdown("**Medical Information**")
                        st.info(f"""
                        **Medications:** {patient.get('Current_Medications', 'None')}  
                        **Drug Allergies:** {patient.get('Drug_Allergies', 'None')}  
                        **Other Allergies:** {patient.get('Other_Allergies', 'None')}  
                        **Recent Surgeries:** {patient.get('Recent_Surgeries', 'None')}  
                        **Medical Devices:** {patient.get('Medical_Devices', 'None')}
                        """)
                        
                        st.markdown("**Emergency Status**")
                        status = patient.get('Emergency_Status', 'None')
                        if status and status != 'None':
                            st.error(f"⚠️ {status}")
                        else:
                            st.success("✓ No active alerts")
                
                # TAB 2: QR Code & NFC
                with tab2:
                    st.markdown("### 🔳 Your Emergency QR Code")
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown("**QR Code**")
                        st.caption("Scan this in emergencies")
                        
                        # Generate QR
                        qr_bytes = generate_emergency_qr(patient['Patient_ID'])
                        st.image(qr_bytes, width=300)
                        
                        # Download QR
                        st.download_button(
                            "⬇️ Download QR Code",
                            data=qr_bytes,
                            file_name=f"Emergency_QR_{patient['Patient_ID']}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    
                    with col2:
                        st.markdown("**Public Emergency Link**")
                        st.caption("For NFC card programming")
                        
                        public_link = get_public_link(patient['Patient_ID'])
                        
                        st.code(public_link, language=None)
                        
                        # Copy button (simulated)
                        if st.button("📋 Copy Link", use_container_width=True):
                            st.success("✅ Link copied! (Use the code box above)")
                        
                        st.divider()
                        
                        st.markdown("**How to Use:**")
                        st.markdown("""
                        1. **Print QR Code** → Carry in wallet
                        2. **Program NFC Card** → Use link above
                        3. **Emergency** → Scan/Tap for instant access
                        """)
                    
                    st.divider()
                    
                    with st.expander("📱 How to Program NFC Card"):
                        st.markdown(get_nfc_instructions())
                
                # TAB 3: Download PDF
                with tab3:
                    st.markdown("### 📄 Complete Medical History PDF")
                    
                    st.info("""
                    This PDF contains your complete medical information:
                    - Personal details
                    - Medical history
                    - Allergies & medications
                    - Emergency contacts
                    - QR code for quick access
                    """)
                    
                    col1, col2, col3 = st.columns([1,2,1])
                    
                    with col2:
                        # Generate PDF
                        pdf_bytes = generate_medical_pdf(patient)
                        
                        st.download_button(
                            "📥 Download Complete Medical PDF",
                            data=pdf_bytes,
                            file_name=f"Medical_Report_{patient['Patient_ID']}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary"
                        )
                        
                        st.caption("🔒 Keep this document secure and confidential")
            
            elif response.status_code == 404:
                st.error("❌ Patient ID not found. Please check and try again.")
            else:
                st.error(f"⚠️ Server error: {response.status_code}")
        
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The server may be waking up (free tier). Try again in 30 seconds.")
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")

elif search_btn:
    st.warning("⚠️ Please enter your Patient ID")

st.divider()

# Help section
with st.expander("❓ Need Help?"):
    st.markdown("""
    ### Frequently Asked Questions
    
    **Where do I get my Patient ID?**  
    Your Patient ID is provided when you register. Contact your administrator if you don't have it.
    
    **How do I use the QR code?**  
    1. Download the QR code image
    2. Print it or save on your phone
    3. In emergencies, responders can scan it to access your info
    
    **How do I program an NFC card?**  
    1. Get an NFC tag (available online)
    2. Download "NFC Tools" app
    3. Copy the public link and write it to the card
    
    **Is my data secure?**  
    Yes, only people with your Patient ID or QR code can access your emergency information.
    """)

st.caption("Emergency Health Locker v1.0")