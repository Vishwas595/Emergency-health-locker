const mongoose = require("mongoose");

const PatientSchema = new mongoose.Schema(
  {
    Patient_ID: {
      type: String,
      required: true,
      unique: true
    },

    Name: { type: String },
    Date_of_Birth: { type: String },
    Gender: { type: String },

    Blood_Type: { type: String },
    Emergency_Contacts: { type: String },

    Current_Medications: { type: String, default: "" },
    Drug_Allergies: { type: String, default: "" },
    Other_Allergies: { type: String, default: "None" },

    Recent_Surgeries: { type: String, default: "None" },
    Medical_Devices: { type: String, default: "None" },

    Emergency_Status: { type: String },
    Vital_Signs_Last_Recorded: { type: String },

    Recent_Lab_Findings: { type: String },

    DNR_Status: { type: Boolean, default: false },
    Organ_Donor: { type: Boolean, default: false }
  },
  { timestamps: true }
);

module.exports = mongoose.model("Patient", PatientSchema);
