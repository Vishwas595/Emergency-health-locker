// ===============================
// ENV CONFIG (MUST BE FIRST)
// ===============================
require("dotenv").config();

// ===============================
// IMPORTS
// ===============================
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const multer = require("multer");

const Patient = require("./models/Patient");
const MedicalRecord = require("./models/MedicalRecord");

// 🔴 PDF GENERATOR (THIS FIXES YOUR ISSUE)
const generateMedicalPDF = require("./utils/pdfGenerator");

const app = express();

// ===============================
// BASIC MIDDLEWARE
// ===============================
app.use(express.json());
app.use(cors());

// ===============================
// ENV VALIDATION
// ===============================
if (!process.env.MONGO_URI) {
  console.error("❌ MONGO_URI missing");
  process.exit(1);
}

if (!process.env.ADMIN_SECRET) {
  console.error("❌ ADMIN_SECRET missing");
  process.exit(1);
}

// ===============================
// HEALTH CHECK
// ===============================
app.get("/", (req, res) => {
  res.send("🚑 Emergency Health Locker Backend Running");
});

// ===============================
// ADMIN AUTH
// ===============================
const adminAuth = (req, res, next) => {
  const key = req.headers["x-admin-key"];
  if (!key || key !== process.env.ADMIN_SECRET) {
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
  .catch(err => {
    console.error("❌ MongoDB failed:", err.message);
    process.exit(1);
  });

// ===============================
// MULTER (FILE UPLOAD)
// ===============================
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 15 * 1024 * 1024 }
});

// =====================================================
// 👤 USER REGISTER / UPDATE
// =====================================================
app.post("/api/user/patients", async (req, res) => {
  try {
    const data = req.body;
    if (!data.Patient_ID) {
      return res.status(400).json({ error: "Patient_ID required" });
    }

    const patient = await Patient.findOneAndUpdate(
      { Patient_ID: data.Patient_ID },
      data,
      { new: true, upsert: true }
    );

    res.status(200).json(patient);
  } catch (err) {
    res.status(500).json({ error: "Failed to save patient" });
  }
});

// =====================================================
// 👤 GET PATIENT BY ID
// =====================================================
app.get("/api/patients/:id", async (req, res) => {
  try {
    const patient = await Patient.findOne({ Patient_ID: req.params.id });
    if (!patient) {
      return res.status(404).json({ error: "Patient not found" });
    }
    res.json(patient);
  } catch {
    res.status(500).json({ error: "Error fetching patient" });
  }
});

// =====================================================
// 🔒 ADMIN – GET ALL PATIENTS
// =====================================================
app.get("/api/patients", adminAuth, async (req, res) => {
  try {
    const patients = await Patient.find();
    res.json({ patients });
  } catch {
    res.status(500).json({ error: "Failed to fetch patients" });
  }
});

// =====================================================
// 📁 MEDICAL RECORDS
// =====================================================
app.post("/api/records/upload", upload.single("file"), async (req, res) => {
  try {
    const { Patient_ID, Record_Type, Record_Title, Uploaded_By } = req.body;

    if (!Patient_ID || !Record_Type || !Record_Title || !req.file) {
      return res.status(400).json({ error: "Missing fields" });
    }

    const record = new MedicalRecord({
      Patient_ID,
      Record_Type,
      Record_Title,
      File_Name: req.file.originalname,
      File_Mime_Type: req.file.mimetype,
      File_Data: req.file.buffer,
      File_Size: req.file.size,
      Uploaded_By: Uploaded_By || "User"
    });

    await record.save();
    res.status(201).json({ message: "Uploaded", id: record._id });
  } catch {
    res.status(500).json({ error: "Upload failed" });
  }
});

app.get("/api/records/:patientId", async (req, res) => {
  try {
    const records = await MedicalRecord.find(
      { Patient_ID: req.params.patientId },
      { File_Data: 0 }
    );
    res.json(records);
  } catch {
    res.status(500).json({ error: "Fetch failed" });
  }
});

app.get("/api/records/download/:id", async (req, res) => {
  try {
    const record = await MedicalRecord.findById(req.params.id);
    if (!record) return res.status(404).json({ error: "File not found" });

    res.set({
      "Content-Type": record.File_Mime_Type,
      "Content-Disposition": `attachment; filename="${record.File_Name}"`
    });

    res.send(record.File_Data);
  } catch {
    res.status(500).json({ error: "Download failed" });
  }
});

// =====================================================
// 🌍 PUBLIC EMERGENCY DATA
// =====================================================
app.get("/api/public/:id", async (req, res) => {
  try {
    const patient = await Patient.findOne(
      { Patient_ID: req.params.id },
      {
        Name: 1,
        Blood_Type: 1,
        Emergency_Contacts: 1,
        Emergency_Status: 1,
        Current_Medications: 1,
        Drug_Allergies: 1
      }
    );

    if (!patient) {
      return res.status(404).json({ error: "Patient not found" });
    }

    res.json(patient);
  } catch {
    res.status(500).json({ error: "Emergency fetch failed" });
  }
});

// =====================================================
// 📄 PDF DOWNLOAD (🔥 FIXED PART)
// =====================================================
app.get("/api/pdf/:id", async (req, res) => {
  try {
    const patient = await Patient.findOne({ Patient_ID: req.params.id });

    if (!patient) {
      return res.status(404).send("Patient not found");
    }

    // Create PDF using your pdfGenerator.js
    const pdfBuffer = await generateMedicalPDF(patient);

    res.setHeader("Content-Type", "application/pdf");
    res.setHeader(
      "Content-Disposition",
      `inline; filename=Medical_${req.params.id}.pdf`
    );

    res.send(pdfBuffer);
  } catch (err) {
    console.error("PDF ERROR:", err);
    res.status(500).send("PDF generation failed");
  }
});

// ===============================
// START SERVER
// ===============================
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
