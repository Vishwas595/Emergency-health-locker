// server.js
const express = require("express");
const mongoose = require("mongoose");
const Patient = require("./models/Patient");

const app = express();
app.use(express.json());

mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("✅ MongoDB connected"))
  .catch(err => console.log("❌ DB Connection error:", err));

// GET all patients
app.get("/api/patients", async (req, res) => {
  const patients = await Patient.find();
  res.json({ patients });
});

// GET single patient by ID
app.get("/api/patients/:id", async (req, res) => {
  const patient = await Patient.findOne({ Patient_ID: req.params.id });
  if (!patient) return res.status(404).json({ error: "Patient not found" });
  res.json(patient);
});

// POST new patient
app.post("/api/patients", async (req, res) => {
  const patient = new Patient(req.body);
  await patient.save();
  res.status(201).json(patient);
});

app.listen(5000, () => console.log("🚀 Server running on http://localhost:5000"));
