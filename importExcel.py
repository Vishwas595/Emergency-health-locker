from pymongo import MongoClient
import random

# ======================================
# CONFIGURATION
# ======================================

# 🔐 SAME MongoDB URI used in backend
MONGO_URI = "mongodb+srv://vishwavarshaa7_db_user:ZQYT2zUjdac4qJbG@cluster0.ogxvqwx.mongodb.net/quickmedic"

DATABASE_NAME = None          # None = use DB from URI
COLLECTION_NAME = "patients"

# ======================================
# RANDOM NAME DATA
# ======================================

FIRST_NAMES = [
    "Arjun", "Karthik", "Rohit", "Suresh", "Vikram",
    "Anand", "Ramesh", "Prakash", "Naveen", "Santhosh",
    "Aditi", "Priya", "Kavya", "Divya", "Meena",
    "Anjali", "Pooja", "Keerthi", "Lakshmi", "Nithya"
]

LAST_NAMES = [
    "Kumar", "Sharma", "Reddy", "Iyer", "Nair",
    "Patel", "Gupta", "Singh", "Das", "Rao",
    "Menon", "Chatterjee", "Banerjee", "Malhotra"
]

# ======================================
# MIGRATION LOGIC
# ======================================

def generate_random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def main():
    client = MongoClient(MONGO_URI)

    if DATABASE_NAME:
        db = client[DATABASE_NAME]
    else:
        db = client.get_database()

    patients = db[COLLECTION_NAME]

    # 🔎 Find names like "Patient 1", "Patient 2", etc.
    query = {
        "Name": { "$regex": "^Patient\\s\\d+", "$options": "i" }
    }

    cursor = patients.find(query)

    updated = 0

    for patient in cursor:
        new_name = generate_random_name()

        patients.update_one(
            {"_id": patient["_id"]},
            {
                "$set": {
                    "Name": new_name,
                    "Last_Updated": "random_name_migration"
                }
            }
        )

        updated += 1
        print(
            f"Updated Patient_ID={patient.get('Patient_ID')} "
            f"→ Name='{new_name}'"
        )

    print("\n======================================")
    print("✅ NAME MIGRATION COMPLETED")
    print(f"👤 Total patients updated: {updated}")
    print("======================================\n")

    client.close()

# ======================================
# ENTRY POINT
# ======================================

if __name__ == "__main__":
    main()
