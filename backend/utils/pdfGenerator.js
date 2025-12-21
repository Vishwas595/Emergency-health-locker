const PDFDocument = require("pdfkit");
const fs = require("fs");
const path = require("path");

module.exports = function generateMedicalPDF(patient) {
  return new Promise((resolve) => {
    const doc = new PDFDocument({ margin: 40 });
    const buffers = [];

    doc.on("data", buffers.push.bind(buffers));
    doc.on("end", () => resolve(Buffer.concat(buffers)));

    // ===============================
    // WATERMARK LOGO
    // ===============================
    const logoPath = path.join(__dirname, "../assets/qure_logo.png");
    if (fs.existsSync(logoPath)) {
      doc.opacity(0.08);
      doc.image(logoPath, 150, 200, { width: 300 });
      doc.opacity(1);
    }

    // ===============================
    // HEADER
    // ===============================
    doc.fontSize(20).fillColor("red").text("EMERGENCY MEDICAL PROFILE", {
      align: "center",
    });

    doc.moveDown(0.5);
    doc.fontSize(10).fillColor("black").text("FOR EMERGENCY USE ONLY", {
      align: "center",
    });

    doc.moveDown(2);

    // ===============================
    // PERSONAL INFO
    // ===============================
    doc.fontSize(14).text("PERSONAL INFORMATION", { underline: true });
    doc.moveDown(0.5);

    const field = (label, value) =>
      doc.fontSize(11).text(`${label}: ${value || "N/A"}`);

    field("Patient ID", patient.Patient_ID);
    field("Name", patient.Name);
    field("Gender", patient.Gender);
    field("Blood Group", patient.Blood_Type);
    field("Emergency Contact", patient.Emergency_Contacts);

    doc.moveDown();

    // ===============================
    // CRITICAL MEDICAL INFO
    // ===============================
    doc.fontSize(14).fillColor("red").text("CRITICAL MEDICAL INFORMATION", {
      underline: true,
    });
    doc.fillColor("black").moveDown(0.5);

    field("Current Medications", patient.Current_Medications);
    field("Drug Allergies", patient.Drug_Allergies);
    field("Other Allergies", patient.Other_Allergies);
    field("Medical Devices", patient.Medical_Devices);
    field("Recent Surgeries", patient.Recent_Surgeries);

    doc.moveDown();

    // ===============================
    // FOOTER
    // ===============================
    doc.fontSize(9).fillColor("gray").text(
      "⚠️ Confidential medical information.\nUse only for emergency medical care.\nPowered by QURE.",
      { align: "center" }
    );

    doc.end();
  });
};
