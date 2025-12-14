from pymongo import MongoClient
import math

# 🔐 MongoDB connection
MONGO_URI = "mongodb+srv://vishwavarshaa7_db_user:ZQYT2zUjdac4qJbG@cluster0.ogxvqwx.mongodb.net/"
client = MongoClient(MONGO_URI)

db = client["quickmedic"]
patients = db["patients"]

# 🔁 Update all documents
for patient in patients.find():

    updates = {}

    # Fix NaN values
    for field in [
        "Current_Medications",
        "Recent_Surgeries",
        "Drug_Allergies",
        "Other_Allergies",
        "Medical_Devices",
        "Emergency_Status"
    ]:
        if field in patient and (
            patient[field] is None or
            patient[field] == "NaN" or
            (isinstance(patient[field], float) and math.isnan(patient[field]))
        ):
            updates[field] = ""

    # Add new structured fields (if not present)
    if "Medical_History" not in patient:
        updates["Medical_History"] = []

    if "Uploaded_Files" not in patient:
        updates["Uploaded_Files"] = []

    if "Last_Updated" not in patient:
        updates["Last_Updated"] = "system_migration"

    if updates:
        patients.update_one(
            {"_id": patient["_id"]},
            {"$set": updates}
        )

print("✅ Database migration completed successfully")
