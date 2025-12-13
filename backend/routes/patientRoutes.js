router.get("/patients", async (req, res) => {
  const patients = await Patient.find();
  console.log("Patients found:", patients.length);
  res.json({ patients });
});
