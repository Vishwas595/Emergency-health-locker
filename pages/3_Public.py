import streamlit as st
import requests
from utils.pdf_generator import generate_medical_pdf

st.set_page_config(
    page_title="Emergency Medical Information",
    page_icon="🚑",
    layout="wide"
)

BACKEND_URL = "https://emergency-health-locker.onrender.com/api/patients"

# ========================================
# THIS PAGE IS WHAT QR CODE OPENS
# ========================================

st.markdown("""
<style>
    .emergency-header {
        background-color: #ff4444;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .critical-info {
        background-color: #fff3cd;
        border-left: 5px solid #ff9800;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="emergency-header"><h1>🚑 EMERGENCY MEDICAL INFORMATION</h1><p>For Emergency Use Only</p></div>', unsafe_allow_html=True)

# Get patient ID from URL parameter
patient_id = st.query_params.get("patient_id")

if not patient_id:
    st.error("❌ **Invalid Access**")
    st.warning("This page requires a valid patient ID. Please scan the QR code or use the NFC card.")
    st.stop()

# Fetch patient data
with st.spinner("Loading emergency information..."):
    try:
        response = requests.get(
            f"https://emergency-health-locker.onrender.com/api/public/{patient_id}",timeout=10)

        
        if response.status_code == 200:
            patient = response.json()
            
            # ========================================
            # EMERGENCY INFORMATION DISPLAY
            # ========================================
            
            st.success(f"✅ Emergency record loaded for: **{patient.get('Name', 'Unknown')}**")
            
            st.divider()
            
            # Critical Information - Top Section
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="PATIENT ID",
                    value=patient.get('Patient_ID', 'N/A')
                )
            
            with col2:
                blood_type = patient.get('Blood_Type', 'N/A')
                st.metric(
                    label="BLOOD TYPE",
                    value=blood_type
                )
            
            with col3:
                st.metric(
                    label="AGE/DOB",
                    value=patient.get('Date_of_Birth', 'N/A')
                )
            
            with col4:
                st.metric(
                    label="GENDER",
                    value=patient.get('Gender', 'N/A')
                )
            
            st.divider()
            
            # Emergency Alert (if any)
            emergency_status = patient.get('Emergency_Status')
            if emergency_status and emergency_status not in ['None', 'N/A', '']:
                st.error(f"⚠️ **CRITICAL ALERT:** {emergency_status}")
            
            # Two column layout for detailed info
            col_left, col_right = st.columns(2)
            
            with col_left:
                # ALLERGIES - CRITICAL
                st.markdown("### 🚨 ALLERGIES")
                with st.container(border=True):
                    drug_allergies = patient.get('Drug_Allergies', 'None')
                    other_allergies = patient.get('Other_Allergies', 'None')
                    
                    if drug_allergies != 'None':
                        st.error(f"**Drug Allergies:** {drug_allergies}")
                    else:
                        st.success("**Drug Allergies:** None")
                    
                    if other_allergies != 'None':
                        st.warning(f"**Other Allergies:** {other_allergies}")
                    else:
                        st.info("**Other Allergies:** None")
                
                # MEDICATIONS
                st.markdown("### 💊 CURRENT MEDICATIONS")
                with st.container(border=True):
                    medications = patient.get('Current_Medications', 'None')
                    if medications != 'None':
                        st.info(medications)
                    else:
                        st.success("No current medications")
                
                # MEDICAL DEVICES
                st.markdown("### 🔧 MEDICAL DEVICES")
                with st.container(border=True):
                    devices = patient.get('Medical_Devices', 'None')
                    if devices != 'None':
                        st.warning(f"⚠️ {devices}")
                    else:
                        st.success("None")
            
            with col_right:
                # EMERGENCY CONTACT
                st.markdown("### 📞 EMERGENCY CONTACT")
                with st.container(border=True):
                    contact = patient.get('Emergency_Contacts', 'Not available')
                    st.info(f"**Contact Number:** {contact}")
                
                # RECENT SURGERIES
                st.markdown("### 🏥 RECENT SURGERIES")
                with st.container(border=True):
                    surgeries = patient.get('Recent_Surgeries', 'None')
                    if surgeries != 'None':
                        st.info(surgeries)
                    else:
                        st.success("No recent surgeries")
                
                # VITAL SIGNS (Last Recorded)
                st.markdown("### 📊 LAST VITAL SIGNS")
                with st.container(border=True):
                    vitals = patient.get('Vital_Signs_Last_Recorded', 'Not recorded')
                    st.info(vitals)
            
            st.divider()
            
            # Important Status Indicators
            col_a, col_b = st.columns(2)
            
            with col_a:
                dnr = patient.get('DNR_Status', False)
                if dnr:
                    st.error("⚠️ **DNR Status:** DO NOT RESUSCITATE")
                else:
                    st.success("✓ **DNR Status:** Not specified")
            
            with col_b:
                donor = patient.get('Organ_Donor', False)
                if donor:
                    st.info("💚 **Organ Donor:** Yes")
                else:
                    st.info("**Organ Donor:** Not registered")
            
            st.divider()
            
            # Download Complete Medical History
            st.markdown("### 📄 Complete Medical History")
            
            st.info("""
            For detailed medical history, download the full PDF report below.
            This contains comprehensive information not shown on this emergency page.
            """)
            
            # Generate and provide PDF download
            try:
                pdf_bytes = generate_medical_pdf(patient)
                
                col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
                
                with col_pdf2:
                    st.download_button(
                        "📥 Download Complete Medical PDF",
                        data=pdf_bytes,
                        file_name=f"Emergency_Medical_Report_{patient_id}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary"
                    )
            except Exception as e:
                st.error(f"Unable to generate PDF: {str(e)}")
            
            st.divider()
            
            # Footer notice
            st.warning("""
            ⚠️ **NOTICE TO EMERGENCY PERSONNEL:**
            
            This information is provided for emergency medical use only.
            All information should be verified with the patient when possible.
            For complete medical history, please download the PDF above.
            """)
            
        elif response.status_code == 404:
            st.error("❌ **Patient Record Not Found**")
            st.warning(f"No record exists for Patient ID: **{patient_id}**")
            st.info("Please verify the QR code or NFC card is correctly programmed.")
        
        else:
            st.error(f"⚠️ **Server Error:** Unable to retrieve patient information (Status: {response.status_code})")
    
    except requests.exceptions.Timeout:
        st.error("⏱️ **Request Timed Out**")
        st.warning("The server is taking longer than expected. This may happen on free-tier hosting after periods of inactivity.")
        st.info("Please wait 30 seconds and refresh the page.")
    
    except Exception as e:
        st.error(f"❌ **Connection Error:** {str(e)}")
        st.warning("Unable to connect to the medical database. Please try again.")

st.divider()
st.caption("QCURE v1.0 | For Emergency Use Only")