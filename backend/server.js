// server.js
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const multer = require("multer");

const Patient = require("./models/Patient");
const MedicalRecord = require("./models/MedicalRecord");

const app = express();
const upload = multer();

// ===============================
// BASIC MIDDLEWARE
// ===============================
app.use(express.json());
app.use(cors());

// ===============================
// ROOT ROUTE (Health Check)
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
// ADMIN ROUTES
// ===============================

// 🔒 Admin – Get ALL patients
app.get("/api/patients", adminAuth, async (req, res) => {
  try {
    const patients = await Patient.find();
    res.json({ patients });
  } catch {
    res.status(500).json({ error: "Failed to fetch patients" });
  }
});

// 🔒 Admin – Create NEW patient
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
// USER ROUTES (PHASE 2A)
// ===============================

// 👤 User – Create OR Update patient
app.post("/api/user/patients", async (req, res) => {
  try {
    const patient = await Patient.findOneAndUpdate(
      { Patient_ID: req.body.Patient_ID },
      req.body,
      { new: true, upsert: true }
    );
    res.status(200).json(patient);
  } catch {
    res.status(500).json({ error: "Failed to save patient" });
  }
});

// 👤 User/Admin – Get patient by ID (FULL DATA)
app.get("/api/patients/:id", async (req, res) => {
  try {
    const patient = await Patient.findOne({ Patient_ID: req.params.id });
    if (!patient) return res.status(404).json({ error: "Patient not found" });
    res.json(patient);
  } catch {
    res.status(500).json({ error: "Error fetching patient" });
  }
});

// ===============================
// 📁 PHASE 2B – MEDICAL RECORD ROUTES
// ===============================

// 📤 Upload medical document
app.post("/api/records/upload", upload.single("file"), async (req, res) => {
  try {
    const { Patient_ID, Record_Type, Record_Title, Uploaded_By } = req.body;

    if (!Patient_ID || !Record_Type || !Record_Title || !req.file) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    const record = new MedicalRecord({
      Patient_ID,
      Record_Type,
      Record_Title,
      File_Name: req.file.originalname,
      File_Mime: req.file.mimetype,
      File_Data: req.file.buffer,
      Uploaded_By: Uploaded_By || "User"
    });

    await record.save();
    res.status(201).json({ message: "Medical record uploaded successfully" });
  } catch (err) {
    res.status(500).json({ error: "Failed to upload medical record" });
  }
});

// 📂 List records by Patient_ID
app.get("/api/records/:patientId", async (req, res) => {
  try {
    const records = await MedicalRecord.find(
      { Patient_ID: req.params.patientId },
      { File_Data: 0 }
    ).sort({ Uploaded_At: -1 });

    res.json(records);
  } catch {
    res.status(500).json({ error: "Failed to fetch records" });
  }
});

// ⬇️ Download record
app.get("/api/records/download/:id", async (req, res) => {
  try {
    const record = await MedicalRecord.findById(req.params.id);
    if (!record) return res.status(404).send("File not found");

    res.set({
      "Content-Type": record.File_Mime,
      "Content-Disposition": `attachment; filename="${record.File_Name}"`
    });

    res.send(record.File_Data);
  } catch {
    res.status(500).send("Failed to download file");
  }
});

// ===============================
// 🌍 PUBLIC EMERGENCY ROUTE
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
        Current_Medications: 1,
        Medical_Devices: 1,
        Recent_Surgeries: 1,
      }
    );

    if (!patient) return res.status(404).json({ error: "Patient not found" });
    res.json(patient);
  } catch {
    res.status(500).json({ error: "Error fetching emergency data" });
  }
});

// ===============================
// START SERVER
// ===============================
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
