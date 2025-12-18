// server.js
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const Patient = require("./models/Patient");

const app = express();

app.use(express.json());
app.use(cors());

// Health check
app.get("/", (req, res) => {
  res.send("🚑 Emergency Health Locker Backend is Running");
});

// Admin auth
const adminAuth = (req, res, next) => {
  const adminKey = req.headers["x-admin-key"];
  if (!adminKey || adminKey !== process.env.ADMIN_SECRET) {
    return res.status(401).json({ error: "Unauthorized admin access" });
  }
  next();
};

// MongoDB
mongoose
  .connect(process.env.MONGO_URI)
  .then(() => console.log("✅ MongoDB connected"))
  .catch((err) => console.error(err));

// ===============================
// ADMIN ROUTES
// ===============================
app.get("/api/patients", adminAuth, async (req, res) => {
  const patients = await Patient.find();
  res.json({ patients });
});

app.post("/api/patients", adminAuth, async (req, res) => {
  try {
    const patient = new Patient(req.body);
    await patient.save();
    res.status(201).json(patient);
  } catch {
    res.status(400).json({ error: "Failed to create patient" });
  }
});

// ===============================
// USER ROUTES (THIS FIXES YOUR ISSUE)
// ===============================
app.get("/api/patients/:id", async (req, res) => {
  const patient = await Patient.findOne({ Patient_ID: req.params.id });
  if (!patient) return res.status(404).json({ error: "Patient not found" });
  res.json(patient);
});

app.post("/api/user/patients", async (req, res) => {
  try {
    const patient = await Patient.findOneAndUpdate(
      { Patient_ID: req.body.Patient_ID },
      req.body,
      { new: true, upsert: true }
    );
    res.json(patient);
  } catch {
    res.status(500).json({ error: "Failed to save patient" });
  }
});

// ===============================
// PUBLIC EMERGENCY
// ===============================
app.get("/api/public/:id", async (req, res) => {
  const patient = await Patient.findOne(
    { Patient_ID: req.params.id },
    {
      Name: 1,
      Blood_Type: 1,
      Emergency_Contacts: 1,
      Current_Medications: 1,
      Drug_Allergies: 1,
      Emergency_Status: 1,
    }
  );

  if (!patient) return res.status(404).json({ error: "Patient not found" });
  res.json(patient);
});

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
