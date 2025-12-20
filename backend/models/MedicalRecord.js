const mongoose = require("mongoose");

const MedicalRecordSchema = new mongoose.Schema({
  Patient_ID: {
    type: String,
    required: true,
    index: true
  },

  Record_Type: {
    type: String,
    enum: ["Lab Report", "Prescription", "Medical Report", "Scan"],
    required: true
  },

  Record_Title: {
    type: String,
    required: true
  },

  File_Name: {
    type: String,
    required: true
  },

  File_Mime: {
    type: String,
    required: true
  },

  File_Data: {
    type: Buffer,
    required: true
  },

  Uploaded_By: {
    type: String,
    enum: ["User", "Admin"],
    default: "User"
  },

  Uploaded_At: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model("MedicalRecord", MedicalRecordSchema);
