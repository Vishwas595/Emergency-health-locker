const mongoose = require("mongoose");

const MedicalRecordSchema = new mongoose.Schema(
  {
    // 🔗 Link to patient
    Patient_ID: {
      type: String,
      required: true,
      index: true
    },

    // 📂 Type of medical record
    Record_Type: {
      type: String,
      enum: ["Lab Report", "Prescription", "Medical Report", "Scan", "Other"],
      required: true
    },

    Record_Title: {
      type: String,
      required: true
    },

    // 📄 File details
    File_Name: {
      type: String,
      required: true
    },

    File_Mime_Type: {
      type: String,
      required: true
    },

    File_Data: {
      type: Buffer,
      required: true
    },

    File_Size: {
      type: Number
    },

    // 👤 Uploader info
    Uploaded_By: {
      type: String,
      enum: ["User", "Admin"],
      default: "User"
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model("MedicalRecord", MedicalRecordSchema);
