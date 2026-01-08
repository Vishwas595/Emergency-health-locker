const express = require("express");
const router = express.Router();
const axios = require("axios");

// MODELS
const Patient = require("../models/Patient");
const MedicalRecord = require("../models/MedicalRecord");

/*
  RULE-BASED INTENT DETECTION (FALLBACK)
*/
function detectIntent(message) {
  const msg = message
    .toLowerCase()
    .replace(/[^a-z\s]/g, "");

  if (
    msg.includes("blood") ||
    msg.includes("blood group") ||
    msg.includes("blood type")
  ) {
    return "GET_BLOOD_GROUP";
  }

  if (
    msg.includes("allergy") ||
    msg.includes("allergies")
  ) {
    return "GET_ALLERGIES";
  }

  if (
    msg.includes("medicine") ||
    msg.includes("medication")
  ) {
    return "GET_MEDICATIONS";
  }

  if (
    msg.includes("summary") ||
    msg.includes("profile")
  ) {
    return "GET_PROFILE_SUMMARY";
  }

  if (
    msg.includes("latest report") ||
    msg.includes("recent report")
  ) {
    return "GET_LATEST_REPORT";
  }

  if (
    msg.includes("report") ||
    msg.includes("records")
  ) {
    return "GET_REPORT_LIST";
  }

  if (
    msg.includes("diagnose") ||
    msg.includes("diagnosis") ||
    msg.includes("treat") ||
    msg.includes("treatment") ||
    msg.includes("am i") ||
    msg.includes("do i have") ||
    msg.includes("diabetic") ||
    msg.includes("diabetes")
  ) {
    return "UNSAFE_MEDICAL_REQUEST";
  }

  return "UNKNOWN";
}

/*
  CHATBOT MESSAGE HANDLER
*/
router.post("/message", async (req, res) => {
  try {
    const { message, patientId } = req.body;

    if (!message || !message.trim() || !patientId) {
      return res.status(400).json({
        success: false,
        reply: "Message or patient context missing."
      });
    }

    // ===============================
    // 🧠 BIOBERT INTENT DETECTION
    // ===============================
    let intent = "UNKNOWN";

    try {
      const aiResponse = await axios.post(
        "http://localhost:8000/predict",
        { message }
      );

      intent = aiResponse.data.intent;
    } catch (err) {
      console.error("BioBERT service error, falling back to rules");
      intent = detectIntent(message);
    }

    // ===============================
    // 🚨 BLOCK UNSAFE MEDICAL REQUESTS
    // ===============================
    if (intent === "UNSAFE_MEDICAL_REQUEST") {
      return res.json({
        success: true,
        reply:
          "I can’t help with medical diagnosis or treatment advice. Please consult a qualified healthcare professional."
      });
    }

    // ===============================
    // 🩸 BLOOD GROUP
    // ===============================
    if (intent === "GET_BLOOD_GROUP") {
      const patient = await Patient.findOne(
        { Patient_ID: patientId },
        { Blood_Type: 1 }
      );

      return res.json({
        success: true,
        reply: patient?.Blood_Type
          ? `Your blood group is ${patient.Blood_Type}.`
          : "Blood group information is not available in your profile."
      });
    }

    // ===============================
    // 🚫 ALLERGIES
    // ===============================
    if (intent === "GET_ALLERGIES") {
      const patient = await Patient.findOne(
        { Patient_ID: patientId },
        { Drug_Allergies: 1, Other_Allergies: 1 }
      );

      return res.json({
        success: true,
        reply:
          `Drug allergies: ${patient?.Drug_Allergies || "None listed"}.\n` +
          `Other allergies: ${patient?.Other_Allergies || "None listed"}.`
      });
    }

    // ===============================
    // 💊 MEDICATIONS
    // ===============================
    if (intent === "GET_MEDICATIONS") {
      const patient = await Patient.findOne(
        { Patient_ID: patientId },
        { Current_Medications: 1 }
      );

      return res.json({
        success: true,
        reply: patient?.Current_Medications
          ? `Your current medications are: ${patient.Current_Medications}.`
          : "No current medications are listed."
      });
    }

    // ===============================
    // 📋 PROFILE SUMMARY
    // ===============================
    if (intent === "GET_PROFILE_SUMMARY") {
      const patient = await Patient.findOne({ Patient_ID: patientId });

      if (!patient) {
        return res.json({
          success: true,
          reply: "Your medical profile is not found."
        });
      }

      return res.json({
        success: true,
        reply:
          `Profile summary:\n` +
          `Blood Group: ${patient.Blood_Type || "N/A"}\n` +
          `Medications: ${patient.Current_Medications || "N/A"}\n` +
          `Drug Allergies: ${patient.Drug_Allergies || "N/A"}`
      });
    }

    // ===============================
    // 📄 LATEST REPORT
    // ===============================
    if (intent === "GET_LATEST_REPORT") {
      const record = await MedicalRecord.findOne(
        { Patient_ID: patientId },
        { File_Data: 0 }
      ).sort({ createdAt: -1 });

      return res.json({
        success: true,
        reply: record
          ? `Your latest report is "${record.Record_Title}" (${record.Record_Type}).`
          : "No medical reports found."
      });
    }

    // ===============================
    // 📂 REPORT LIST
    // ===============================
    if (intent === "GET_REPORT_LIST") {
      const count = await MedicalRecord.countDocuments({
        Patient_ID: patientId
      });

      return res.json({
        success: true,
        reply:
          count > 0
            ? `You have ${count} medical records uploaded.`
            : "You have not uploaded any medical records."
      });
    }

    // ===============================
    // 🤷 UNKNOWN
    // ===============================
    return res.json({
      success: true,
      reply:
        "I can help you with your medical profile and uploaded reports. Try asking about blood group, allergies, medications, or reports."
    });

  } catch (err) {
    console.error("Chatbot error:", err);
    res.status(500).json({
      success: false,
      reply: "Chatbot service error. Please try again."
    });
  }
});

module.exports = router;
