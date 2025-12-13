const mongoose = require("mongoose");

const patientSchema = new mongoose.Schema({
  Patient_ID: String,
  Name: String,
  Date_of_Birth: String,
  Gender: String,
  Blood_Type: String,
  Emergency_Contacts: Number,
  Current_Medications: String,
  Drug_Allergies: String,
  Other_Allergies: String,
  Recent_Surgeries: String,
  Vital_Signs_Last_Recorded: String,
  Emergency_Status: String,
  DNR_Status: Boolean,
  Organ_Donor: Boolean,
  Medical_Devices: String
});

module.exports = mongoose.model("Patient", patientSchema);
