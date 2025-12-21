const API_BASE = "https://emergency-health-locker.onrender.com/api";

// ================= AUTH =================
const patientId = localStorage.getItem("patient_id");
const role = localStorage.getItem("role");

if (!patientId || role !== "USER") {
  window.location.href = "index.html";
}

// ================= LOGOUT =================
function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}

// ================= LOAD PROFILE =================
async function loadProfile() {
  const res = await fetch(`${API_BASE}/patients/${patientId}`);
  if (!res.ok) return;

  const p = await res.json();

  name.value = p.Name || "";
  dob.value = p.Date_of_Birth || "";
  gender.value = p.Gender || "Male";
  blood.value = p.Blood_Type || "";
  emergency_contact.value = p.Emergency_Contacts || "";
  medications.value = p.Current_Medications || "";
  drug_allergies.value = p.Drug_Allergies || "";
  other_allergies.value = p.Other_Allergies || "";
  surgeries.value = p.Recent_Surgeries || "";
  emergency_status.value = p.Emergency_Status || "";
  vitals.value = p.Vital_Signs_Last_Recorded || "";
  devices.value = p.Medical_Devices || "";

  loadEmergency();
  loadRecords();
}

loadProfile();

// ================= SAVE PROFILE =================
async function saveProfile() {
  const payload = {
    Patient_ID: patientId,
    Name: name.value,
    Date_of_Birth: dob.value,
    Gender: gender.value,
    Blood_Type: blood.value,
    Emergency_Contacts: emergency_contact.value,
    Current_Medications: medications.value,
    Drug_Allergies: drug_allergies.value,
    Other_Allergies: other_allergies.value,
    Recent_Surgeries: surgeries.value,
    Emergency_Status: emergency_status.value,
    Vital_Signs_Last_Recorded: vitals.value,
    Medical_Devices: devices.value
  };

  const res = await fetch(`${API_BASE}/user/patients`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  profileMsg.innerText = res.ok
    ? "✅ Profile updated"
    : "❌ Update failed";
}

// ================= UPLOAD RECORD =================
async function uploadRecord() {
  const file = recordFile.files[0];
  if (!file || !recordTitle.value) {
    uploadMsg.innerText = "Title & file required";
    return;
  }

  const form = new FormData();
  form.append("file", file);
  form.append("Patient_ID", patientId);
  form.append("Record_Type", recordType.value);
  form.append("Record_Title", recordTitle.value);
  form.append("Uploaded_By", "User");

  const res = await fetch(`${API_BASE}/records/upload`, {
    method: "POST",
    body: form
  });

  uploadMsg.innerText = res.status === 201
    ? "✅ Record uploaded"
    : "❌ Upload failed";

  loadRecords();
}

// ================= LOAD RECORDS =================
async function loadRecords() {
  const res = await fetch(`${API_BASE}/records/${patientId}`);
  if (!res.ok) return;

  const data = await res.json();
  records.innerHTML = "";

  if (!data.length) {
    records.innerHTML = "<p>No records uploaded.</p>";
    return;
  }

  data.forEach(r => {
    records.innerHTML += `
      <div>
        <strong>${r.Record_Title}</strong><br>
        ${r.Record_Type} • ${r.File_Name}<br>
        <a href="${API_BASE}/records/download/${r._id}" target="_blank">⬇️ Download</a>
        <hr>
      </div>
    `;
  });
}

// ================= EMERGENCY =================
function loadEmergency() {
  qrImage.src = `${API_BASE}/qr/${patientId}`;
  publicLink.innerText =
    `${window.location.origin}/public.html?patient_id=${patientId}`;
}

function downloadPDF() {
  window.open(`${API_BASE}/pdf/${patientId}`, "_blank");
}
