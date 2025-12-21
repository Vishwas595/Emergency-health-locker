const API_BASE = "https://emergency-health-locker.onrender.com/api";

// ================= GET PATIENT ID FROM URL =================
const params = new URLSearchParams(window.location.search);
const patientId = params.get("patient_id");

const content = document.getElementById("content");
const pdfBtn = document.getElementById("pdfBtn");

if (!patientId) {
  content.innerHTML = "<p style='color:red'>Invalid access. Scan QR code.</p>";
  throw new Error("No patient ID");
}

// ================= LOAD EMERGENCY DATA =================
async function loadEmergency() {
  try {
    const res = await fetch(`${API_BASE}/public/${patientId}`);
    if (!res.ok) {
      content.innerHTML = "<p style='color:red'>Patient not found</p>";
      return;
    }

    const p = await res.json();

    content.innerHTML = `
      <h2>Patient: ${p.Name || "Unknown"}</h2>
      <p><b>Blood Group:</b> ${p.Blood_Type || "N/A"}</p>
      <p><b>Emergency Contact:</b> ${p.Emergency_Contacts || "N/A"}</p>
    `;

    pdfBtn.style.display = "block";
  } catch (e) {
    content.innerHTML = "<p style='color:red'>Server unavailable</p>";
  }
}

loadEmergency();

// ================= PDF DOWNLOAD =================
pdfBtn.onclick = () => {
  window.open(
    `${API_BASE}/pdf/${patientId}`,
    "_blank"
  );
};
