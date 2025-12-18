const express = require("express");
const router = express.Router();
const Patient = require("../models/Patient");

// ===============================
// ADMIN ROUTES (PROTECTED LATER)
// ===============================

// Get all patients (Admin)
router.get("/patients", async (req, res) => {
  try {
    const patients = await Patient.find();
    res.json(patients);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch patients" });
  }
});

// Get patient by ID (Admin/User)
router.get("/patients/:id", async (req, res) => {
  try {
    const patient = await Patient.findOne({
      Patient_ID: req.params.id
    });

    if (!patient) {
      return res.status(404).json({ error: "Patient not found" });
    }

    res.json(patient);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch patient" });
  }
});

// ===============================
// USER CREATE / UPDATE PATIENT
// (NO ADMIN CHECK – PHASE 2A)
// ===============================
router.post("/user/patients", async (req, res) => {
  try {
    const patient = await Patient.findOneAndUpdate(
      { Patient_ID: req.body.Patient_ID },
      req.body,
      { new: true, upsert: true }
    );
    res.status(200).json(patient);
  } catch (err) {
    res.status(500).json({ error: "Failed to save patient" });
  }
});


// ===============================
// PUBLIC EMERGENCY ROUTE
// ===============================
router.get("/public/:id", async (req, res) => {
  try {
    const patient = await Patient.findOne(
      { Patient_ID: req.params.id },
      {
        Name: 1,
        Blood_Type: 1,
        Emergency_Contacts: 1,
        Current_Medications: 1,
        Drug_Allergies: 1,
        Emergency_Status: 1,
        Recent_Lab_Findings: 1
      }
    );

    if (!patient) {
      return res.status(404).json({ error: "Patient not found" });
    }

    res.json(patient);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch emergency data" });
  }
});

module.exports = router;
