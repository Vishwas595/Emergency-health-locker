import streamlit as st
import requests
from utils.pdf_generator import generate_medical_pdf

st.set_page_config(page_title="Admin Panel | QURE", page_icon="🛠️", layout="wide")

API_PATIENTS = "https://emergency-health-locker.onrender.com/api/patients"
API_RECORDS = "https://emergency-health-locker.onrender.com/api/records"

# ===============================
# AUTH CHECK
# ===============================
if not st.session_state.get("logged_in") or st.session_state.get("role") != "ADMIN":
    st.error("Unauthorized")
    st.stop()

ADMIN_SECRET = st.secrets.get("ADMIN_SECRET", "admin123")
HEADERS = {"x-admin-key": ADMIN_SECRET}

st.title("🛠️ Admin Panel")
st.divider()

# ===============================
# FETCH PATIENTS
# ===============================
res = requests.get(API_PATIENTS, headers=HEADERS)
patients = res.json().get("patients", []) if res.status_code == 200 else []

st.success(f"Total Patients: {len(patients)}")

search = st.text_input("Search by ID or Name")
if search:
    search = search.lower()
    patients = [
        p for p in patients
        if search in (p.get("Patient_ID","")+p.get("Name","")).lower()
    ]

# ===============================
# PATIENT LIST + MEDICAL HISTORY
# ===============================
for p in patients:
    with st.container(border=True):
        st.markdown(f"### {p.get('Name','Unknown')}")
        pid = p.get("Patient_ID")
        st.caption(f"Patient ID: {pid}")
        st.text(f"Blood: {p.get('Blood_Type','-')}")
        st.text(f"Gender: {p.get('Gender','-')}")

        if p.get("Emergency_Status"):
            st.warning(p["Emergency_Status"])

        # 🔽 MEDICAL HISTORY
        with st.expander("📁 View Medical History"):
            if not pid:
                st.info("No patient ID")
            else:
                r = requests.get(f"{API_RECORDS}/{pid}", headers=HEADERS)
                if r.status_code == 200:
                    records = r.json()
                    if not records:
                        st.info("No records uploaded")
                    else:
                        for rec in records:
                            col1, col2 = st.columns([3,1])
                            with col1:
                                st.markdown(f"**{rec['Record_Title']}**")
                                st.caption(f"{rec['Record_Type']} • {rec['File_Name']}")
                            with col2:
                                st.markdown(
                                    f"[⬇️ Download]({API_RECORDS}/download/{rec['_id']})",
                                    unsafe_allow_html=True
                                )

                # 📄 FULL SUMMARY PDF
                pdf = generate_medical_pdf(p)
                st.download_button(
                    "📄 Download Medical Summary PDF",
                    pdf,
                    file_name=f"{pid}_summary.pdf",
                    mime="application/pdf"
                )
