// server.js
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const Patient = require("./models/Patient");

const app = express();
app.use(express.json());
app.use(cors());

// ===============================
// ROOT ROUTE (Render health check)
// ===============================
app.get("/", (req, res) => {
  res.send("🚑 Emergency Health Locker Backend is Running");
});

// ===============================
// MongoDB Connection
// ===============================
mongoose
  .connect(process.env.MONGO_URI)
  .then(() => console.log("✅ MongoDB connected"))
  .catch((err) => console.error("❌ MongoDB error:", err));

// ===============================
// ADMIN / USER ROUTES
// ===============================

// Get ALL patients (admin)
app.get("/api/patients", async (req, res) => {
  try {
    const patients = await Patient.find();
    res.json({ patients });
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch patients" });
  }
});

// Get ONE patient (admin / user)
app.get("/api/patients/:id", async (req, res) => {
  try {
    const patient = await Patient.findOne({ Patient_ID: req.params.id });
    if (!patient) {
      return res.status(404).json({ error: "Patient not found" });
    }
    res.json(patient);
  } catch (err) {
    res.status(500).json({ error: "Error fetching patient" });
  }
});

// Add NEW patient (admin)
app.post("/api/patients", async (req, res) => {
  try {
    const patient = new Patient(req.body);
    await patient.save();
    res.status(201).json(patient);
  } catch (err) {
    res.status(400).json({ error: "Failed to create patient" });
  }
});

// ===============================
// PUBLIC EMERGENCY ROUTE (QR / NFC)
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
        Organ_Donor: 1
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
// START SERVER (ALWAYS LAST)
// ===============================
const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
