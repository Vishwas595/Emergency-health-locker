from fpdf import FPDF
import tempfile
import os
from utils.qr_generator import generate_emergency_qr


LOGO_PATH = "assets/qure_logo.png"


def add_watermark(pdf):
    """
    Add QURE logo watermark at center of page
    """
    if not os.path.exists(LOGO_PATH):
        return

    # Save current position
    x = pdf.get_x()
    y = pdf.get_y()

    # Light grey effect (fake opacity)
    pdf.set_text_color(220, 220, 220)

    # Center watermark
    pdf.image(
        LOGO_PATH,
        x=55,     # center X
        y=80,     # center Y
        w=100     # large but faded look
    )

    # Restore cursor
    pdf.set_xy(x, y)
    pdf.set_text_color(0, 0, 0)


def generate_medical_pdf(patient):
    """
    Generate PDF (used for BOTH emergency & medical view)
    """

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ===============================
    # WATERMARK (FIRST)
    # ===============================
    add_watermark(pdf)

    # ===============================
    # HEADER
    # ===============================
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 15, "EMERGENCY MEDICAL PROFILE", ln=True, align="C")

    pdf.set_font("Arial", "I", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 5, "FOR EMERGENCY USE ONLY", ln=True, align="C")

    pdf.set_draw_color(200, 0, 0)
    pdf.set_line_width(0.6)
    pdf.line(10, 35, 200, 35)
    pdf.ln(12)

    # ===============================
    # PERSONAL INFORMATION
    # ===============================
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "PERSONAL INFORMATION", ln=True, fill=True)
    pdf.ln(3)

    personal_info = [
        ("Patient ID", patient.get("Patient_ID", "N/A")),
        ("Full Name", patient.get("Name", "N/A")),
        ("Date of Birth", patient.get("Date_of_Birth", "N/A")),
        ("Gender", patient.get("Gender", "N/A")),
        ("Blood Group", patient.get("Blood_Type", "N/A")),
    ]

    for label, value in personal_info:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(60, 8, f"{label}:", 0)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, str(value), ln=True)

    pdf.ln(5)

    # ===============================
    # 🚨 CRITICAL MEDICAL INFORMATION
    # ===============================
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(255, 220, 220)
    pdf.cell(0, 10, "CRITICAL MEDICAL INFORMATION", ln=True, fill=True)
    pdf.ln(3)

    critical_medical = [
        ("Current Medications", patient.get("Current_Medications", "None")),
        ("Drug Allergies", patient.get("Drug_Allergies", "None")),
        ("Other Allergies", patient.get("Other_Allergies", "None")),
        ("Medical Devices", patient.get("Medical_Devices", "None")),
        ("Recent Surgeries", patient.get("Recent_Surgeries", "None")),
    ]

    for label, value in critical_medical:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(60, 8, f"{label}:", 0)
        pdf.set_font("Arial", "", 11)

        text = str(value) if value else "None"
        if len(text) > 50:
            pdf.ln(8)
            pdf.multi_cell(0, 6, text)
        else:
            pdf.cell(0, 8, text, ln=True)

    pdf.ln(5)

    # ===============================
    # 🚑 EMERGENCY STATUS
    # ===============================
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(255, 180, 180)
    pdf.cell(0, 10, "EMERGENCY STATUS", ln=True, fill=True)
    pdf.ln(3)

    emergency_info = [
        ("Emergency Condition", patient.get("Emergency_Status", "None")),
        ("Emergency Contact", patient.get("Emergency_Contacts", "N/A")),
        ("Last Vital Signs", patient.get("Vital_Signs_Last_Recorded", "N/A")),
        ("DNR Status", "YES" if patient.get("DNR_Status") else "NO"),
        ("Organ Donor", "YES" if patient.get("Organ_Donor") else "NO"),
    ]

    for label, value in emergency_info:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(60, 8, f"{label}:", 0)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, str(value), ln=True)

    # ===============================
    # QR CODE (BOTTOM RIGHT)
    # ===============================
    try:
        qr = generate_emergency_qr(patient.get("Patient_ID", ""))
        qr_bytes = qr.getvalue() if hasattr(qr, "getvalue") else qr

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(qr_bytes)
            path = tmp.name

        pdf.image(path, x=155, y=230, w=40)
        os.remove(path)

    except Exception as e:
        print("QR error:", e)

    # ===============================
    # FOOTER
    # ===============================
    pdf.ln(10)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(
        0,
        5,
        "⚠️ Confidential medical information.\n"
        "Use only for emergency medical care.\n"
        "Powered by QURE.",
    )

    return pdf.output(dest="S").encode("latin1")
