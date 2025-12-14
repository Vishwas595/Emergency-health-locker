const mongoose = require("mongoose");

const PatientSchema = new mongoose.Schema(
  {
    Patient_ID: { type: String, required: true, unique: true },
    Name: String,
    Date_of_Birth: String,
    Gender: String,
    Blood_Type: String,

    Emergency_Contacts: String,

    Current_Medications: { type: String, default: "None" },
    Drug_Allergies: { type: String, default: "None" },
    Other_Allergies: { type: String, default: "None" },

    Recent_Surgeries: { type: String, default: "None" },
    Medical_Devices: { type: String, default: "None" },

    Vital_Signs_Last_Recorded: String,
    Emergency_Status: String,

    DNR_Status: Boolean,
    Organ_Donor: Boolean,

    Public_Enabled: { type: Boolean, default: true }
  },
  { timestamps: true }
);

module.exports = mongoose.model("Patient", PatientSchema);
