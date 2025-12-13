import qrcode
from io import BytesIO

# Your Streamlit Cloud URL
APP_URL = "https://emergency-health-locker-jvaaiwgtsr3u8iwxscdebb.streamlit.app"

def generate_emergency_qr(patient_id):
    """
    Generate QR code that opens the Public Emergency page
    
    Args:
        patient_id: Patient ID (e.g., "P001")
    
    Returns:
        BytesIO: QR code image as bytes
    """
    
    # QR contains ONLY the public emergency URL
    # NO medical data inside QR
    emergency_url = f"{APP_URL}/3_🚑_Public?patient_id={patient_id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    
    qr.add_data(emergency_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return buf

def get_public_link(patient_id):
    """Get the public emergency link for NFC card"""
    return f"{APP_URL}/3_🚑_Public?patient_id={patient_id}"

def get_nfc_instructions():
    """Return instructions for programming NFC card"""
    return """
    ### 📱 How to Program Your NFC Card
    
    1. **Get an NFC Tag** (NTAG213 or similar)
    2. **Download NFC Tools** app on your phone
    3. **Open NFC Tools** → Write
    4. **Add a Record** → URL/URI
    5. **Paste the link** shown above
    6. **Write** → Tap your NFC card
    7. **Done!** Your card is now programmed
    
    ⚡ When tapped, the NFC card will open the emergency page directly.
    """