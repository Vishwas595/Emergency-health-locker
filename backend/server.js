// server.js
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const Patient = require("./models/Patient");

const app = express();

// ===============================
// BASIC MIDDLEWARE
// ===============================
app.use(express.json());
app.use(cors());

// ===============================
// ROOT ROUTE (Render health check)
// ===============================
app.get("/", (req, res) => {
  res.send("🚑 Emergency Health Locker Backend is Running");
});

// ===============================
// ADMIN AUTH MIDDLEWARE
// ===============================
const adminAuth = (req, res, next) => {
  const adminKey = req.headers["x-admin-key"];

  if (!adminKey || adminKey !== process.env.ADMIN_SECRET) {
    return res.status(401).json({ error: "Unauthorized admin access" });
  }

  next();
};

// ===============================
// MONGODB CONNECTION
// ===============================
mongoose
  .connect(process.env.MONGO_URI)
  .then(() => console.log("✅ MongoDB connected"))
  .catch((err) => console.error("❌ MongoDB connection error:", err));

// ===============================
// ADMIN / USER ROUTES
// ===============================

// 🔒 ADMIN – Get ALL patients
app.get("/api/patients", adminAuth, async (req, res) => {
  try {
    const patients = await Patient.find();
    res.json({ patients });
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch patients" });
  }
});

// 👤 USER / ADMIN – Get ONE patient by ID
app.get("/api/patients/:id", async (req, res) => {
  try {
    const patient = await Patient.findOne({
      Patient_ID: req.params.id,
    });

    if (!patient) {
      return res.status(404).json({ error: "Patient not found" });
    }

    res.json(patient);
  } catch (err) {
    res.status(500).json({ error: "Error fetching patient" });
  }
});

// 🔒 ADMIN – Add NEW patient
app.post("/api/patients", adminAuth, async (req, res) => {
  try {
    const patient = new Patient(req.body);
    await patient.save();
    res.status(201).json(patient);
  } catch (err) {
    res.status(400).json({ error: "Failed to create patient" });
  }
});

// ===============================
// 🌍 PUBLIC EMERGENCY ROUTE (QR / NFC)
// ===============================
app.get("/api/public/:id", async (req, res) => {
  try {
    const patient = await Patient.findOne(
      { Patient_ID: req.params.id },
      {
        Patient_ID: 1,
        Name: 1,
        Date_of_Birth: 1,
        Gender: 1,
        Blood_Type: 1,
        Emergency_Contacts: 1,
        Emergency_Status: 1,
        Drug_Allergies: 1,
        Other_Allergies: 1,
        Current_Medications: 1,
        Medical_Devices: 1,
        Recent_Surgeries: 1,
        Vital_Signs_Last_Recorded: 1,
        DNR_Status: 1,
        Organ_Donor: 1,
      }
    );

    if (!patient) {
      return res.status(404).json({ error: "Patient not found" });
    }

    res.json(patient);
  } catch (err) {
    res.status(500).json({ error: "Error fetching emergency data" });
  }
});

// ===============================
// START SERVER (RENDER SAFE)
// ===============================
const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
