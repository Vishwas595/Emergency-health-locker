from fpdf import FPDF
import tempfile
import os
from utils.qr_generator import generate_emergency_qr

def generate_medical_pdf(patient):
    """
    Generate complete medical history PDF
    
    Args:
        patient: Dictionary with patient data
    
    Returns:
        bytes: PDF file as bytes
    """
    
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 15, "EMERGENCY MEDICAL PROFILE", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 5, "For Emergency Use Only", ln=True, align='C')
    
    # Line separator
    pdf.set_draw_color(200, 0, 0)
    pdf.set_line_width(0.5)
    pdf.line(10, 35, 200, 35)
    
    pdf.ln(15)
    
    # Personal Information Section
    pdf.set_font("Arial", 'B', 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "PERSONAL INFORMATION", ln=True, fill=True)
    pdf.ln(2)
    
    pdf.set_font("Arial", '', 11)
    info_fields = [
        ("Patient ID", patient.get('Patient_ID', 'N/A')),
        ("Full Name", patient.get('Name', 'N/A')),
        ("Date of Birth", patient.get('Date_of_Birth', 'N/A')),
        ("Gender", patient.get('Gender', 'N/A')),
        ("Blood Type", patient.get('Blood_Type', 'N/A'))
    ]
    
    for label, value in info_fields:
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(60, 8, f"{label}:", 0)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, str(value), ln=True)
    
    pdf.ln(5)
    
    # Medical Information Section
    pdf.set_font("Arial", 'B', 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "MEDICAL INFORMATION", ln=True, fill=True)
    pdf.ln(2)
    
    pdf.set_font("Arial", '', 11)
    medical_fields = [
        ("Current Medications", patient.get('Current_Medications', 'None')),
        ("Drug Allergies", patient.get('Drug_Allergies', 'None')),
        ("Other Allergies", patient.get('Other_Allergies', 'None')),
        ("Recent Surgeries", patient.get('Recent_Surgeries', 'None')),
        ("Medical Devices", patient.get('Medical_Devices', 'None'))
    ]
    
    for label, value in medical_fields:
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(60, 8, f"{label}:", 0)
        pdf.set_font("Arial", '', 11)
        # Handle long text
        if str(value) != 'None' and len(str(value)) > 50:
            pdf.ln(8)
            pdf.multi_cell(0, 6, str(value))
        else:
            pdf.cell(0, 8, str(value), ln=True)
    
    pdf.ln(5)
    
    # Emergency Information Section
    pdf.set_font("Arial", 'B', 14)
    pdf.set_fill_color(255, 200, 200)
    pdf.cell(0, 10, "EMERGENCY INFORMATION", ln=True, fill=True)
    pdf.ln(2)
    
    pdf.set_font("Arial", '', 11)
    emergency_fields = [
        ("Emergency Status", patient.get('Emergency_Status', 'None')),
        ("Emergency Contact", patient.get('Emergency_Contacts', 'N/A')),
        ("Vital Signs (Last)", patient.get('Vital_Signs_Last_Recorded', 'N/A')),
        ("DNR Status", "Yes" if patient.get('DNR_Status') else "No"),
        ("Organ Donor", "Yes" if patient.get('Organ_Donor') else "No")
    ]
    
    for label, value in emergency_fields:
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(60, 8, f"{label}:", 0)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, str(value), ln=True)
    
    # Add QR Code
    try:
        qr_img = generate_emergency_qr(patient['Patient_ID'])
        temp_file = ""
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            temp_file = tmp.name
            with open(temp_file, 'wb') as f:
                f.write(qr_img.read())
        
        # Position QR in top right
        pdf.image(temp_file, x=155, y=45, w=40)
        
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
    except Exception as e:
        print(f"Error adding QR to PDF: {e}")
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, 
        "This document contains confidential medical information. "
        "Use only for emergency medical care. Scan QR code for digital access.")
    
    # Convert to bytes
    return pdf.output(dest='S').encode('latin1')