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
// Used by: USER (own records) & ADMIN
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
        message: "Patient_ID, Record_Type, Record_Title and file are required"
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

    return res.status(201).json({
      message: "Medical record uploaded successfully",
      recordId: record._id
    });

  } catch (error) {
    console.error("UPLOAD RECORD ERROR:", error);
    return res.status(500).json({ message: "Upload failed" });
  }
});

// ===============================
// 2️⃣ LIST RECORDS BY PATIENT ID
// ===============================
// Used by: USER (own ID) & ADMIN (any ID)
router.get("/records/:patientId", async (req, res) => {
  try {
    const { patientId } = req.params;

    if (!patientId) {
      return res.status(400).json({ message: "Patient ID required" });
    }

    const records = await MedicalRecord.find(
      { Patient_ID: patientId },
      { File_Data: 0 } // ❌ Exclude heavy binary data
    ).sort({ createdAt: -1 });

    return res.status(200).json(records);

  } catch (error) {
    console.error("FETCH RECORDS ERROR:", error);
    return res.status(500).json({ message: "Fetch failed" });
  }
});

// ===============================
// 3️⃣ DOWNLOAD MEDICAL RECORD
// ===============================
// Used by: USER (own record) & ADMIN
router.get("/records/download/:id", async (req, res) => {
  try {
    const { id } = req.params;

    const record = await MedicalRecord.findById(id);

    if (!record) {
      return res.status(404).json({ message: "File not found" });
    }

    res.set({
      "Content-Type": record.File_Mime_Type,
      "Content-Disposition": `attachment; filename="${record.File_Name}"`
    });

    return res.send(record.File_Data);

  } catch (error) {
    console.error("DOWNLOAD RECORD ERROR:", error);
    return res.status(500).json({ message: "Download failed" });
  }
});

module.exports = router;
