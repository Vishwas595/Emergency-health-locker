const QRCode = require("qrcode");

async function generateQRCode(patientID) {
  try {
    const url = `http://localhost:5000/api/patients/${patientID}`;
    const qr = await QRCode.toDataURL(url);
    return qr; // Base64 QR image
  } catch (err) {
    console.error(err);
  }
}

module.exports = generateQRCode;
