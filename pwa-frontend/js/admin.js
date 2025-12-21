const API_PATIENTS = "https://emergency-health-locker.onrender.com/api/patients";
const API_RECORDS = "https://emergency-health-locker.onrender.com/api/records";

// ================= AUTH =================
const role = localStorage.getItem("role");
if (role !== "ADMIN") {
  window.location.href = "index.html";
}

// ================= LOGOUT =================
function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}

// ================= LOAD PATIENTS =================
let allPatients = [];

async function loadPatients() {
  const res = await fetch(API_PATIENTS);
  if (!res.ok) return;

  const data = await res.json();
  allPatients = data.patients || [];
  count.innerText = allPatients.length;
  renderPatients(allPatients);
}

loadPatients();

// ================= RENDER PATIENTS =================
function renderPatients(list) {
  patients.innerHTML = "";

  if (!list.length) {
    patients.innerHTML = "<p>No patients found</p>";
    return;
  }

  list.forEach(p => {
    const pid = p.Patient_ID;

    patients.innerHTML += `
      <div style="border:1px solid #ccc;padding:10px;margin:10px 0">
        <h3>${p.Name || "Unknown"}</h3>
        <p><b>Patient ID:</b> ${pid}</p>
        <p><b>Blood:</b> ${p.Blood_Type || "-"}</p>
        <p><b>Gender:</b> ${p.Gender || "-"}</p>

        ${p.Emergency_Status ? `<p style="color:red">${p.Emergency_Status}</p>` : ""}

        <button onclick="loadRecords('${pid}')">📁 View Medical History</button>
        <button onclick="downloadPDF('${pid}')">📄 Download Summary PDF</button>

        <div id="records-${pid}"></div>
      </div>
    `;
  });
}

// ================= SEARCH =================
function filterPatients() {
  const q = search.value.toLowerCase();
  const filtered = allPatients.filter(p =>
    (p.Patient_ID + p.Name).toLowerCase().includes(q)
  );
  renderPatients(filtered);
}

// ================= LOAD RECORDS =================
async function loadRecords(pid) {
  const container = document.getElementById(`records-${pid}`);
  container.innerHTML = "Loading records...";

  const res = await fetch(`${API_RECORDS}/${pid}`);
  if (!res.ok) {
    container.innerHTML = "Failed to load records";
    return;
  }

  const records = await res.json();
  if (!records.length) {
    container.innerHTML = "<p>No records uploaded</p>";
    return;
  }

  container.innerHTML = "";
  records.forEach(r => {
    container.innerHTML += `
      <div>
        <b>${r.Record_Title}</b><br>
        ${r.Record_Type} • ${r.File_Name}<br>
        <a href="${API_RECORDS}/download/${r._id}" target="_blank">⬇️ Download</a>
        <hr>
      </div>
    `;
  });
}

// ================= PDF =================
function downloadPDF(pid) {
  window.open(
    `https://emergency-health-locker.onrender.com/api/pdf/${pid}`,
    "_blank"
  );
}
