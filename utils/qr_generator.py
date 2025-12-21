from fpdf import FPDF
import tempfile
import os
from utils.qr_generator import generate_emergency_qr


# ===============================
# SAFE VALUE HANDLER (CRITICAL)
# ===============================
def safe(value, fallback="N/A"):
    """
    Convert empty, None, or whitespace-only values
    into a safe medical fallback.
    """
    if value is None:
        return fallback
    if isinstance(value, str) and value.strip() == "":
        return fallback
    return str(value)


# ===============================
# PDF GENERATOR
# ===============================
def generate_medical_pdf(patient):
    """
    Generate complete emergency medical PDF.

    Args:
        patient (dict): Patient data from database

    Returns:
        bytes: PDF file bytes
    """

    pdf = FPDF()
    pdf.add_page()

    # ===============================
    # HEADER
    # ===============================
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 15, "EMERGENCY MEDICAL PROFILE", ln=True, align="C")

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 6, "For Emergency Use Only", ln=True, align="C")

    pdf.set_draw_color(200, 0, 0)
    pdf.set_line_width(0.5)
    pdf.line(10, 35, 200, 35)

    pdf.ln(15)

    # ===============================
    # PERSONAL INFORMATION
    # ===============================
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "PERSONAL INFORMATION", ln=True, fill=True)
    pdf.ln(2)

    personal_fields = [
        ("Patient ID", safe(patient.get("Patient_ID"))),
        ("Full Name", safe(patient.get("Name"))),
        ("Date of Birth", safe(patient.get("Date_of_Birth"))),
        ("Gender", safe(patient.get("Gender"))),
        ("Blood Type", safe(patient.get("Blood_Type"))),
    ]

    for label, value in personal_fields:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(60, 8, f"{label}:", 0)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, value, ln=True)

    pdf.ln(5)

    # ===============================
    # MEDICAL INFORMATION
    # ===============================
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "MEDICAL INFORMATION", ln=True, fill=True)
    pdf.ln(2)

    medical_fields = [
        ("Current Medications", safe(patient.get("Current_Medications"))),
        ("Drug Allergies", safe(patient.get("Drug_Allergies"))),
        ("Other Allergies", safe(patient.get("Other_Allergies"))),
        ("Recent Surgeries", safe(patient.get("Recent_Surgeries"))),
        ("Medical Devices", safe(patient.get("Medical_Devices"))),
    ]

    for label, value in medical_fields:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(60, 8, f"{label}:", 0)
        pdf.set_font("Arial", "", 11)

        if len(value) > 50:
            pdf.ln(8)
            pdf.multi_cell(0, 6, value)
        else:
            pdf.cell(0, 8, value, ln=True)

    pdf.ln(5)

    # ===============================
    # EMERGENCY INFORMATION
    # ===============================
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(255, 220, 220)
    pdf.cell(0, 10, "EMERGENCY INFORMATION", ln=True, fill=True)
    pdf.ln(2)

    emergency_fields = [
        ("Emergency Status", safe(patient.get("Emergency_Status"))),
        ("Emergency Contact", safe(patient.get("Emergency_Contacts"))),
        ("Vital Signs (Last)", safe(patient.get("Vital_Signs_Last_Recorded"))),
        ("DNR Status", "Yes" if patient.get("DNR_Status") else "No"),
        ("Organ Donor", "Yes" if patient.get("Organ_Donor") else "No"),
    ]

    for label, value in emergency_fields:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(60, 8, f"{label}:", 0)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, value, ln=True)

    # ===============================
    # QR CODE (SAFE HANDLING)
    # ===============================
    try:
        qr_obj = generate_emergency_qr(patient.get("Patient_ID", ""))

        # BytesIO safe handling
        if hasattr(qr_obj, "getvalue"):
            qr_bytes = qr_obj.getvalue()
        else:
            qr_bytes = qr_obj

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(qr_bytes)
            temp_path = tmp.name

        pdf.image(temp_path, x=155, y=45, w=40)
        os.remove(temp_path)

    except Exception as e:
        print("⚠️ QR code not added:", e)

    # ===============================
    # FOOTER
    # ===============================
    pdf.ln(10)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(
        0,
        5,
        "This document contains confidential medical information.\n"
        "Use only for emergency medical care.\n"
        "Scan the QR code for real-time digital access.",
    )

    # ===============================
    # RETURN PDF
    # ===============================
    return pdf.output(dest="S").encode("latin1")
