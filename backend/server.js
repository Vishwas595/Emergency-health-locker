// server.js
const express = require("express");
const mongoose = require("mongoose");
const Patient = require("./models/Patient");

const app = express();
app.use(express.json());
const cors = require("cors");
app.use(cors());

// ===============================
// ✅ ROOT ROUTE (VERY IMPORTANT)
// ===============================
app.get("/", (req, res) => {
  res.send("🚑 Emergency Health Locker Backend is Running");
});

// ===============================
// ✅ MONGODB CONNECTION
// ===============================
mongoose
  .connect(process.env.MONGO_URI)
  .then(() => console.log("✅ MongoDB connected"))
  .catch((err) => console.error("❌ MongoDB connection error:", err));

// ===============================
// ✅ API ROUTES
// ===============================

// GET all patients
app.get("/api/patients", async (req, res) => {
  try {
    const patients = await Patient.find();
    res.json(patients);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch patients" });
  }
});

// GET single patient by ID
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

// POST new patient
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
// ✅ START SERVER (RENDER SAFE)
// ===============================
const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
