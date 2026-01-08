// ================= API ENDPOINTS =================
const API_BASE = "https://emergency-health-locker.onrender.com/api";
const API_PATIENTS = `${API_BASE}/patients`;
const API_RECORDS = `${API_BASE}/records`;

// 🔐 ADMIN SECRET (TEMP FOR DEMO / PROJECT)
const ADMIN_SECRET = "admin123";

// ================= AUTH CHECK =================
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
  try {
    const res = await fetch(API_PATIENTS, {
      headers: {
        "x-admin-key": ADMIN_SECRET
      }
    });

    if (!res.ok) {
      console.error("Admin auth failed");
      return;
    }

    const data = await res.json();
    allPatients = data.patients || [];

    count.innerText = allPatients.length;
    renderPatients(allPatients);
  } catch (err) {
    console.error("Failed to load patients", err);
  }
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
      <div class="card admin-card">
        <h3>${p.Name || "Unknown"}</h3>
        <p><b>Patient ID:</b> ${pid}</p>
        <p><b>Blood Group:</b> ${p.Blood_Type || "-"}</p>
        <p><b>Gender:</b> ${p.Gender || "-"}</p>

        ${p.Emergency_Status
          ? `<p class="emergency-text">${p.Emergency_Status}</p>`
          : ""
        }

        <button onclick="loadRecords('${pid}')">
          📁 View Medical History
        </button>

        <button onclick="downloadPDF('${pid}')">
          📄 Download Summary PDF
        </button>

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

// ================= LOAD MEDICAL RECORDS =================
async function loadRecords(pid) {
  const container = document.getElementById(`records-${pid}`);
  container.innerHTML = "Loading records...";

  try {
    const res = await fetch(`${API_RECORDS}/${pid}`, {
      headers: {
        "x-admin-key": ADMIN_SECRET
      }
    });

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
        <div class="record">
          <b>${r.Record_Title}</b><br>
          ${r.Record_Type} • ${r.File_Name}<br>
          <a
            href="${API_RECORDS}/download/${r._id}"
            target="_blank"
          >⬇️ Download</a>
          <hr>
        </div>
      `;
    });
  } catch (err) {
    container.innerHTML = "Error loading records";
    console.error(err);
  }
}

// ================= PDF DOWNLOAD (ADMIN) =================
function downloadPDF(pid) {
  fetch(`${API_BASE}/pdf/${pid}`, {
    headers: {
      "x-admin-key": ADMIN_SECRET
    }
  })
    .then(res => {
      if (!res.ok) throw new Error("PDF fetch failed");
      return res.blob();
    })
    .then(blob => {
      const url = URL.createObjectURL(blob);
      window.open(url);
    })
    .catch(err => {
      alert("Failed to download PDF");
      console.error(err);
    });
}
