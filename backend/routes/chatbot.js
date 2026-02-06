const express = require("express");
const router = express.Router();
const axios = require("axios");

// ================= MODELS =================
const Patient = require("../models/Patient");
const MedicalRecord = require("../models/MedicalRecord");

// ================= ENV =================
const BIOBERT_URL =
  process.env.BIOBERT_URL || "http://localhost:8000";

// ==================================================
// 🔁 RULE-BASED INTENT DETECTION (FALLBACK)
// ==================================================
function detectIntent(message) {
  const msg = message.toLowerCase().replace(/[^a-z0-9\s]/g, "");

  if (msg.includes("blood")) return "GET_BLOOD_GROUP";
  if (msg.includes("allergy")) return "GET_ALLERGIES";
  if (msg.includes("medicine") || msg.includes("medication"))
    return "GET_MEDICATIONS";
  if (msg.includes("summary") || msg.includes("profile"))
    return "GET_PROFILE_SUMMARY";
  if (msg.includes("latest report") || msg.includes("recent report"))
    return "GET_LATEST_REPORT";
  if (msg.includes("report") || msg.includes("records"))
    return "GET_REPORT_LIST";

  if (
    msg.includes("diagnose") ||
    msg.includes("treatment") ||
    msg.includes("diabetes") ||
    msg.includes("am i") ||
    msg.includes("do i have")
  ) {
    return "UNSAFE_MEDICAL_REQUEST";
  }

  return "UNKNOWN";
}

// ==================================================
// 💬 CHATBOT MESSAGE ENDPOINT
// ==================================================
router.post("/message", async (req, res) => {
  try {
    const { message, patientId } = req.body;

    if (!message || !patientId) {
      return res.status(400).json({
        success: false,
        reply: "Message or patient context missing.",
      });
    }

    // ==================================================
    // 🧠 BIOBERT INTENT DETECTION
    // ==================================================
    let intent = "UNKNOWN";

    try {
      const aiRes = await axios.post(
        `${BIOBERT_URL}/predict`,
        { message },
        { timeout: 8000 }
      );

      intent = aiRes.data?.intent || "UNKNOWN";
    } catch (err) {
      console.warn("⚠️ BioBERT unavailable → fallback");
      intent = detectIntent(message);
    }

    if (!intent || intent === "UNKNOWN") {
      intent = detectIntent(message);
    }

    // ==================================================
    // 🚨 BLOCK MEDICAL DIAGNOSIS
    // ==================================================
    if (intent === "UNSAFE_MEDICAL_REQUEST") {
      return res.json({
        success: true,
        reply:
          "I can’t provide medical diagnosis or treatment advice. Please consult a qualified doctor.",
      });
    }

    // ==================================================
    // 🩸 BLOOD GROUP
    // ==================================================
    if (intent === "GET_BLOOD_GROUP") {
      const patient = await Patient.findOne(
        { PatientID: patientId },
        { BloodType: 1 }
      );

      return res.json({
        success: true,
        reply: patient?.BloodType
          ? `Your blood group is ${patient.BloodType}.`
          : "Blood group is not available in your profile.",
      });
    }

    // ==================================================
    // 🚫 ALLERGIES
    // ==================================================
    if (intent === "GET_ALLERGIES") {
      const patient = await Patient.findOne(
        { PatientID: patientId },
        { DrugAllergies: 1, OtherAllergies: 1 }
      );

      return res.json({
        success: true,
        reply:
          `Drug allergies: ${patient?.DrugAllergies || "None"}.\n` +
          `Other allergies: ${patient?.OtherAllergies || "None"}.`,
      });
    }

    // ==================================================
    // 💊 MEDICATIONS
    // ==================================================
    if (intent === "GET_MEDICATIONS") {
      const patient = await Patient.findOne(
        { PatientID: patientId },
        { CurrentMedications: 1 }
      );

      return res.json({
        success: true,
        reply: patient?.CurrentMedications
          ? `Your current medications are: ${patient.CurrentMedications}.`
          : "No medications listed.",
      });
    }

    // ==================================================
    // 📋 PROFILE SUMMARY
    // ==================================================
    if (intent === "GET_PROFILE_SUMMARY") {
      const patient = await Patient.findOne({ PatientID: patientId });

      if (!patient) {
        return res.json({
          success: true,
          reply: "Your medical profile was not found.",
        });
      }

      return res.json({
        success: true,
        reply:
          `Profile Summary:\n` +
          `Blood Group: ${patient.BloodType || "N/A"}\n` +
          `Medications: ${patient.CurrentMedications || "N/A"}\n` +
          `Drug Allergies: ${patient.DrugAllergies || "N/A"}`,
      });
    }

    // ==================================================
    // 📄 LATEST REPORT
    // ==================================================
    if (intent === "GET_LATEST_REPORT") {
      const record = await MedicalRecord.findOne(
        { PatientID: patientId },
        { FileData: 0 }
      ).sort({ createdAt: -1 });

      return res.json({
        success: true,
        reply: record
          ? `Your latest report is "${record.RecordTitle}" (${record.RecordType}).`
          : "No medical reports found.",
      });
    }

    // ==================================================
    // 📂 REPORT COUNT
    // ==================================================
    if (intent === "GET_REPORT_LIST") {
      const count = await MedicalRecord.countDocuments({
        PatientID: patientId,
      });

      return res.json({
        success: true,
        reply:
          count > 0
            ? `You have ${count} medical records uploaded.`
            : "You have not uploaded any medical records.",
      });
    }

    // ==================================================
    // 🤖 DEFAULT RESPONSE
    // ==================================================
    return res.json({
      success: true,
      reply:
        "I can help you with blood group, allergies, medications, and medical reports. Try asking about them.",
    });
  } catch (err) {
    console.error("❌ Chatbot error:", err);
    return res.status(500).json({
      success: false,
      reply: "Chatbot service error. Please try again later.",
    });
  }
});

module.exports = router;
