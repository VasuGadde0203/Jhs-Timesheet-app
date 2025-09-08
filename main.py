from fastapi import FastAPI, HTTPException, Depends, status, Body
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import jwt
import secrets
from bson import ObjectId
from bson.errors import InvalidId
import hashlib
from dotenv import load_dotenv
import os 
from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI()

# CORS enable
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Generate a secure JWT secret key
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# MongoDB connection
client = MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
db = client["Timesheets"]
timesheets_collection = db["Timesheet_data"]
sessions_collection = db["sessions"]
employee_details_collection = db["Employee_details"]
client_details_collection = db["Client_details"]

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Pydantic models for request/response validation
class TimesheetEntry(BaseModel):
    employeeId: str
    employeeName: Optional[str] = None
    designation: Optional[str] = None
    gender: Optional[str] = None
    partner: Optional[str] = None
    reportingManager: Optional[str] = None
    department: Optional[str] = None
    weekPeriod: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    projectStartTime: Optional[str] = None
    projectEndTime: Optional[str] = None
    punchIn: Optional[str] = None
    punchOut: Optional[str] = None
    client: Optional[str] = None
    project: Optional[str] = None
    projectCode: Optional[str] = None
    reportingManagerEntry: Optional[str] = None
    activity: Optional[str] = None
    hours: Optional[str] = None
    billable: Optional[str] = None
    remarks: Optional[str] = None

class LoginRequest(BaseModel):
    empid: str
    password: str

class UpdateTimesheetRequest(BaseModel):
    weekPeriod: str
    date: str
    location: Optional[str] = None
    projectStartTime: Optional[str] = None
    projectEndTime: Optional[str] = None
    punchIn: Optional[str] = None
    punchOut: Optional[str] = None
    client: Optional[str] = None
    project: Optional[str] = None
    projectCode: Optional[str] = None
    reportingManagerEntry: Optional[str] = None
    activity: Optional[str] = None
    hours: Optional[str] = None
    billable: Optional[str] = None
    remarks: Optional[str] = None

# Function to create JWT token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to verify JWT token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        employee_id: str = payload.get("sub")
        if employee_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return employee_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


app.mount("/static", StaticFiles(directory="static"), name="static")
# Then, serve HTML from / (adjust as needed)
@app.get("/")
async def root():
    return {"message": "API is running"}  # Or redirect to index.html logic

@app.post("/login")
async def login(login_request: LoginRequest):
    employee = employee_details_collection.find_one({
        "EmpID": login_request.empid.strip()
    })
    if not employee:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Employee ID or Password")
    
    # Simple password validation - password should match empid
    hashed_password = hashlib.sha256(login_request.password.encode()).hexdigest()
    hashed_empid = hashlib.sha256(login_request.empid.encode()).hexdigest()
    if hashed_password != hashed_empid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Employee ID or Password")
    
    # Generate token
    access_token = create_access_token(data={"sub": login_request.empid})
    
    # Store session
    session_data = {
        "employeeId": login_request.empid,
        "token": access_token,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    sessions_collection.insert_one(session_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "success": True,
        "employeeId": login_request.empid
    }

@app.post("/verify_session")
async def verify_session(token: str = Depends(oauth2_scheme)):
    employee_id = await get_current_user(token)
    session = sessions_collection.find_one({"token": token, "employeeId": employee_id})
    if not session or session["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")
    return {"message": "Session valid"}

@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    sessions_collection.delete_one({"token": token})
    return {"message": "Logged out successfully"}

@app.get("/employees")
async def get_employees(current_user: str = Depends(get_current_user)):
    employees = list(employee_details_collection.find({}, {"_id": 0}))
    return employees

@app.get("/clients")
async def get_clients(current_user: str = Depends(get_current_user)):
    clients = list(client_details_collection.find({}, {"_id": 0}))
    return clients

@app.post("/save_timesheets")
async def save_timesheets(entries: List[TimesheetEntry], current_user: str = Depends(get_current_user)):
    print("Received timesheets:", entries)
    collection = timesheets_collection

    if not entries:
        print("No timesheets to save.")
        return {"message": "No data to save", "success": False}

    # Validate that employeeId matches the authenticated user
    for entry in entries:
        if entry.employeeId != current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized employee ID")

    employee_data = {}
    now_iso = datetime.utcnow().isoformat()
    
    for timesheet in entries:
        employee_id = timesheet.employeeId
        week_period = timesheet.weekPeriod

        if employee_id not in employee_data:
            employee_data[employee_id] = {
                "employeeId": timesheet.employeeId,
                "employeeName": timesheet.employeeName or "",
                "designation": timesheet.designation or "",
                "gender": timesheet.gender or "",
                "partner": timesheet.partner or "",
                "reportingManager": timesheet.reportingManager or "",
                "department": timesheet.department or "",
                "Data": {},
                "created_time": now_iso if employee_id not in employee_data else employee_data[employee_id].get("created_time"),
                "updated_time": now_iso
            }

        if week_period not in employee_data[employee_id]["Data"]:
            employee_data[employee_id]["Data"][week_period] = []

        daily_entry = {
            "date": timesheet.date or "",
            "location": timesheet.location or "",
            "projectStartTime": timesheet.projectStartTime or "",
            "projectEndTime": timesheet.projectEndTime or "",
            "punchIn": timesheet.punchIn or "",
            "punchOut": timesheet.punchOut or "",
            "client": timesheet.client or "",
            "project": timesheet.project or "",
            "projectCode": timesheet.projectCode or "",
            "reportingManagerEntry": timesheet.reportingManagerEntry or "",
            "activity": timesheet.activity or "",
            "hours": timesheet.hours or "",
            "billable": timesheet.billable or "",
            "remarks": timesheet.remarks or "",
            "id": str(ObjectId()),  # Unique ID for each entry
            "created_time": now_iso,
            "updated_time": now_iso
        }

        employee_data[employee_id]["Data"][week_period].append(daily_entry)

    print("Processing and saving data to DB...")
    for employee_id, data in employee_data.items():
        # Convert Data dict to list of {week: entries}
        week_list = []
        for week, entries_list in data["Data"].items():
            week_list.append({week: entries_list})
        data["Data"] = week_list

        existing_doc = collection.find_one({"employeeId": employee_id})
        if existing_doc:
            print(f"Updating existing document for employeeId: {employee_id}")
            # Merge Data - existing_doc["Data"] is list of {week: entries}
            existing_weeks = existing_doc.get("Data", [])
            new_weeks = data["Data"]
            
            # For each new week, merge or add
            for new_week_obj in new_weeks:
                week = list(new_week_obj.keys())[0]
                found = False
                for i, existing_item in enumerate(existing_weeks):
                    if isinstance(existing_item, dict) and week in existing_item:
                        existing_weeks[i][week] = new_week_obj[week]
                        found = True
                        break
                if not found:
                    existing_weeks.append(new_week_obj)
            
            # Update the document
            result = collection.update_one(
                {"employeeId": employee_id},
                {"$set": {
                    "Data": existing_weeks,
                    "employeeName": data["employeeName"],
                    "designation": data["designation"],
                    "gender": data["gender"],
                    "partner": data["partner"],
                    "reportingManager": data["reportingManager"],
                    "department": data["department"],
                    "updated_time": now_iso
                }}
            )
            print(f"Updated {result.modified_count} document(s)")
        else:
            print(f"Inserting new document for employeeId: {employee_id}")
            data["created_time"] = now_iso
            result = collection.insert_one(data)
            print(f"Inserted document with ID: {result.inserted_id}")

    return {"message": "Timesheets saved successfully", "employee_ids": list(employee_data.keys()), "success": True}

@app.get("/timesheets/{employee_id}")
async def get_timesheets(employee_id: str, current_user: str = Depends(get_current_user)):
    if employee_id != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access")
    
    try:
        doc = timesheets_collection.find_one({"employeeId": employee_id})
        if not doc:
            return {"success": True, "Data": []}
        
        # Flatten the nested structure for frontend
        flattened_data = []
        
        # Get top-level employee info
        employee_info = {
            "employeeId": doc.get("employeeId", ""),
            "employeeName": doc.get("employeeName", ""),
            "designation": doc.get("designation", ""),
            "gender": doc.get("gender", ""),
            "partner": doc.get("partner", ""),
            "reportingManager": doc.get("reportingManager", ""),
            "department": doc.get("department", "")
        }
        
        # Iterate through Data structure - now a list of {week: [entries]}
        if "Data" in doc and isinstance(doc["Data"], list):
            for week_item in doc["Data"]:
                if isinstance(week_item, dict):
                    week_period = list(week_item.keys())[0]
                    week_entries = week_item.get(week_period, [])
                    if isinstance(week_entries, list):
                        for entry in week_entries:
                            flattened_entry = {**employee_info, **entry}
                            flattened_entry["weekPeriod"] = week_period
                            flattened_data.append(flattened_entry)
        
        return {"success": True, "Data": flattened_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch timesheets: {str(e)}")

@app.put("/update_timesheet/{employee_id}/{entry_id}")
async def update_timesheet(employee_id: str, entry_id: str, update_data: UpdateTimesheetRequest, current_user: str = Depends(get_current_user)):
    print(f"Updating timesheet entry {entry_id} for employee {employee_id} with data: {update_data}")
    if employee_id != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access")
    
    try:
        now_iso = datetime.utcnow().isoformat()
        collection = timesheets_collection
        
        # Find the document
        doc = collection.find_one({"employeeId": employee_id})
        if not doc:
            raise HTTPException(status_code=404, detail="Employee document not found")
        
        entry_found = False
        updated = False
        
        # Search through all weeks and entries - Data is list of {week: [entries]}
        if "Data" in doc and isinstance(doc["Data"], list):
            for week_item in doc["Data"]:
                if isinstance(week_item, dict):
                    week_period = list(week_item.keys())[0]
                    week_entries = week_item.get(week_period, [])
                    if isinstance(week_entries, list):
                        for i, entry in enumerate(week_entries):
                            if entry.get("id") == entry_id:
                                # Update this specific entry
                                updated_entry = {
                                    "date": update_data.date,
                                    "location": update_data.location or entry.get("location", ""),
                                    "projectStartTime": update_data.projectStartTime or entry.get("projectStartTime", ""),
                                    "projectEndTime": update_data.projectEndTime or entry.get("projectEndTime", ""),
                                    "punchIn": update_data.punchIn or entry.get("punchIn", ""),
                                    "punchOut": update_data.punchOut or entry.get("punchOut", ""),
                                    "client": update_data.client or entry.get("client", ""),
                                    "project": update_data.project or entry.get("project", ""),
                                    "projectCode": update_data.projectCode or entry.get("projectCode", ""),
                                    "reportingManagerEntry": update_data.reportingManagerEntry or entry.get("reportingManagerEntry", ""),
                                    "activity": update_data.activity or entry.get("activity", ""),
                                    "hours": update_data.hours or entry.get("hours", ""),
                                    "billable": update_data.billable or entry.get("billable", ""),
                                    "remarks": update_data.remarks or entry.get("remarks", ""),
                                    "updated_time": now_iso,
                                    "id": entry_id  # Keep the same ID
                                }
                                
                                # Replace the entry in the array
                                week_item[week_period][i] = updated_entry
                                updated = True
                                entry_found = True
                                break
                    if updated:
                        break
        
        if not entry_found:
            raise HTTPException(status_code=404, detail="Timesheet entry not found")
        
        # Update the document in database - set the whole Data
        collection.update_one(
            {"employeeId": employee_id},
            {"$set": {
                "Data": doc["Data"],
                "updated_time": now_iso
            }}
        )
        
        return {"success": True, "message": "Timesheet entry updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update timesheet: {str(e)}")
    
