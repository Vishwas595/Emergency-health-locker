import qrcode
from io import BytesIO

# Your Streamlit Cloud URL
APP_URL = "https://emergency-health-locker-jvaaiwgtsr3u8iwxscdebb.streamlit.app"

def generate_emergency_qr(patient_id):
    """
    Generate QR code that opens the Public Emergency page
    """

    # ✅ CORRECT PUBLIC PAGE URL
    emergency_url = f"{APP_URL}/Public?patient_id={patient_id}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(emergency_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return buf


def get_public_link(patient_id):
    """Get the public emergency link for NFC card"""
    return f"{APP_URL}/Public?patient_id={patient_id}"


def get_nfc_instructions():
    return """
    ### 📱 How to Program Your NFC Card

    1. Buy an NFC tag (NTAG213 recommended)
    2. Install **NFC Tools** app
    3. Open app → Write → Add record → URL
    4. Paste the public link
    5. Tap NFC card → Done

    ⚡ Tapping the card opens emergency info instantly
    """
