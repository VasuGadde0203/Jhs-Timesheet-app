# Connect to MongoDB
from pymongo import MongoClient

client = MongoClient("mongodb://45.198.225.149:27017/")
db = client["Timesheets"]

# Create or access a collection
collection = db["Timesheets"]

# Insert a document
data = {
    "employee_id": 101,
    "date": "2025-10-07",
    "hours_worked": 8.5,
    "project": "InsightSpark"
}

collection.insert_one(data)
print("✅ Data inserted successfully!")
