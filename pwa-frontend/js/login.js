const API_BASE = "https://emergency-health-locker.onrender.com/api";

const ADMIN_ID = "ADMIN001";
const ADMIN_PHONE = "7397617895";

function showLogin() {
  document.getElementById("loginBox").style.display = "block";
  document.getElementById("registerBox").style.display = "none";
}

function showRegister() {
  document.getElementById("registerBox").style.display = "block";
  document.getElementById("loginBox").style.display = "none";
}

async function register() {
  const name = regName.value;
  const id = regId.value;
  const phone = regPhone.value;

  if (!name || !id || !phone) {
    msg.innerText = "All fields required";
    return;
  }

  const res = await fetch(`${API_BASE}/user/patients`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      Patient_ID: id,
      Name: name,
      Phone_Number: phone
    })
  });

  msg.innerText = res.ok ? "Registered successfully" : "Registration failed";
}

async function login() {
  const id = loginId.value;
  const phone = loginPhone.value;

  if (!id || !phone) {
    msg.innerText = "Both fields required";
    return;
  }

  // ADMIN
  if (id === ADMIN_ID && phone === ADMIN_PHONE) {
    localStorage.setItem("role", "ADMIN");
    window.location.href = "admin.html";
    return;
  }

  // USER
  const res = await fetch(`${API_BASE}/patients/${id}`);
  if (!res.ok) {
    msg.innerText = "Invalid ID";
    return;
  }

  const data = await res.json();
  if (String(data.Phone_Number) !== phone) {
    msg.innerText = "Incorrect phone number";
    return;
  }

  localStorage.setItem("role", "USER");
  localStorage.setItem("patient_id", id);
  window.location.href = "user.html";
}
