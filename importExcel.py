import pandas as pd
from pymongo import MongoClient

# 1. Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["quickmedic"] # Database
collection = db["patients"] # Collection

# 2. Load Excel file
file_path = r"C:\Users\Lenovo\Downloads\Emergency_Health_Locker_250_Rows.xlsx"
df = pd.read_excel(file_path)

# 3. Convert DataFrame to dictionary
data = df.to_dict(orient="records")

# 4. Insert into MongoDB
if data:
    collection.insert_many(data)
    print(f"✅ Successfully imported {len(data)} rows into MongoDB!")
else:
    print("⚠️ No data found in Excel file.")