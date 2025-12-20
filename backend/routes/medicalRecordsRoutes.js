const express = require("express");
const multer = require("multer");
const MedicalRecord = require("../models/MedicalRecord");

const router = express.Router();

// ===============================
// MULTER CONFIG (IN-MEMORY)
// ===============================
const storage = multer.memoryStorage();

const upload = multer({
  storage,
  limits: {
    fileSize: 15 * 1024 * 1024 // 15 MB
  }
});

// ===============================
// 1️⃣ UPLOAD MEDICAL RECORD
// ===============================
router.post("/records/upload", upload.single("file"), async (req, res) => {
  try {
    const {
      Patient_ID,
      Record_Type,
      Record_Title,
      Uploaded_By
    } = req.body;

    if (!Patient_ID || !Record_Type || !Record_Title || !req.file) {
      return res.status(400).json({
        error: "Patient_ID, Record_Type, Record_Title and file are required"
      });
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

    res.status(201).json({
      message: "Medical record uploaded successfully",
      recordId: record._id
    });
  } catch (err) {
    console.error("Upload error:", err);
    res.status(500).json({ error: "Upload failed" });
  }
});

// ===============================
// 2️⃣ LIST RECORDS BY PATIENT ID
// ===============================
router.get("/records/:patientId", async (req, res) => {
  try {
    const records = await MedicalRecord.find(
      { Patient_ID: req.params.patientId },
      { File_Data: 0 } // ❌ exclude heavy binary
    ).sort({ createdAt: -1 });

    res.json(records);
  } catch (err) {
    console.error("Fetch error:", err);
    res.status(500).json({ error: "Fetch failed" });
  }
});

// ===============================
// 3️⃣ DOWNLOAD MEDICAL RECORD
// ===============================
router.get("/records/download/:id", async (req, res) => {
  try {
    const record = await MedicalRecord.findById(req.params.id);

    if (!record) {
      return res.status(404).json({ error: "File not found" });
    }

    res.set({
      "Content-Type": record.File_Mime_Type,
      "Content-Disposition": `attachment; filename="${record.File_Name}"`
    });

    res.send(record.File_Data);
  } catch (err) {
    console.error("Download error:", err);
    res.status(500).json({ error: "Download failed" });
  }
});

module.exports = router;
