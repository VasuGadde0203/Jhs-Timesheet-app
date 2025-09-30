# from fastapi import FastAPI, HTTPException, Depends, status, Request
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel
# from pymongo import MongoClient
# from typing import List, Optional, Dict
# from datetime import datetime, timedelta
# import jwt
# import secrets
# from bson import ObjectId
# from bson.errors import InvalidId
# import hashlib
# from dotenv import load_dotenv
# import os
# import re
# from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__ident="2b", bcrypt__rounds=12)

# # Load environment variables
# load_dotenv()

# app = FastAPI(title="Professional Time Sheet API", version="1.0.0")

# # CORS middleware - Update allow_origins for production security
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Generate a secure JWT secret key (use environment variable in production)
# SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# # MongoDB connection
# MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
# if not MONGO_CONNECTION_STRING:
#     raise ValueError("MONGO_CONNECTION_STRING environment variable is required")

# client = MongoClient(MONGO_CONNECTION_STRING)
# db = client["Timesheets"]
# timesheets_collection = db["Timesheet_data"]
# sessions_collection = db["sessions"]
# employee_details_collection = db["Employee_details"]
# client_details_collection = db["Client_details"]
# users_collection = db["users"]

# # OAuth2 scheme for token-based authentication
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

# class RegisterRequest(BaseModel):
#     empid: str
#     password: str

# class TimesheetEntry(BaseModel):
#     employeeId: str
#     employeeName: Optional[str] = None
#     designation: Optional[str] = None
#     gender: Optional[str] = None
#     partner: Optional[str] = None
#     reportingManager: Optional[str] = None
#     department: Optional[str] = None
#     weekPeriod: Optional[str] = None
#     date: Optional[str] = None
#     location: Optional[str] = None
#     projectStartTime: Optional[str] = None
#     projectEndTime: Optional[str] = None
#     punchIn: Optional[str] = None
#     punchOut: Optional[str] = None
#     client: Optional[str] = None
#     project: Optional[str] = None
#     projectCode: Optional[str] = None
#     reportingManagerEntry: Optional[str] = None
#     activity: Optional[str] = None
#     hours: Optional[str] = None
#     workingHours: Optional[str] = None
#     billable: Optional[str] = None
#     remarks: Optional[str] = None
#     hits: Optional[str] = None
#     misses: Optional[str] = None
#     feedback_hr: Optional[str] = None
#     feedback_it: Optional[str] = None
#     feedback_crm: Optional[str] = None
#     feedback_others: Optional[str] = None

# class LoginRequest(BaseModel):
#     empid: str
#     password: str

# class UpdateTimesheetRequest(BaseModel):
#     date: str
#     location: Optional[str] = None
#     projectStartTime: Optional[str] = None
#     projectEndTime: Optional[str] = None
#     punchIn: Optional[str] = None
#     punchOut: Optional[str] = None
#     client: Optional[str] = None
#     project: Optional[str] = None
#     projectCode: Optional[str] = None
#     reportingManagerEntry: Optional[str] = None
#     activity: Optional[str] = None
#     hours: Optional[str] = None
#     workingHours: Optional[str] = None
#     billable: Optional[str] = None
#     remarks: Optional[str] = None

# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     print(f"Expires delta: {expires_delta}")
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=1440)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     if not token:
#         print("No token")
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         employee_id: str = payload.get("sub")
#         print(f"Decoded payload: {payload}")
#         if employee_id is None:
#             print("No employee_id")
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
#         print(f"Token: {token}, Employee_id: {employee_id}")
        
#         session = sessions_collection.find_one({
#             "token": token, 
#             "employeeId": employee_id,
#             "expires_at": {"$gt": datetime.utcnow()}
#         })
        
#         if not session:
#             print("No session")
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")
            
#         return employee_id
#     except jwt.PyJWTError:
#         print(f"Error decoding token: {token}")
#         print("Invalid token")
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# # Define frontend path
# frontend_path = os.path.join(os.path.dirname(__file__), "static")
# print("Frontend path:", frontend_path)
# if os.path.exists(frontend_path):
#     print("Files in frontend:", os.listdir(frontend_path))
# else:
#     print(f"Frontend directory not found at: {frontend_path}")

# # Mount static files for assets
# app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# @app.get("/", response_class=FileResponse)
# async def read_root():
#     return FileResponse(os.path.join(frontend_path, "index.html"))

# @app.get("/login", response_class=FileResponse)
# async def login_page():
#     return FileResponse(os.path.join(frontend_path, "login.html"))

# @app.get("/dashboard", response_class=FileResponse)
# async def dashboard_page():
#     return FileResponse(os.path.join(frontend_path, "index.html"))


# @app.post("/register")
# async def register(request: RegisterRequest):
#     empid = request.empid.strip().upper()
#     password = request.password

#     if len(password) < 8:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters")
#     if not re.search(r'[A-Z]', password):
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one uppercase letter")
#     if not re.search(r'[a-z]', password):
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one lowercase letter")
#     if not re.search(r'\d', password):
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one number")
#     if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one special character")

#     employee = employee_details_collection.find_one({"EmpID": empid})
#     if not employee:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee does not exist")

#     existing_user = users_collection.find_one({"empid": empid})
#     if existing_user:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")

#     hashed_password = pwd_context.hash(password)
#     user_data = {
#         "empid": empid,
#         "password": hashed_password
#     }
#     users_collection.insert_one(user_data)

#     return {"success": True, "detail": "Registration successful. Please login."}

# @app.post("/login")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     empid = form_data.username.strip().upper()
#     password = form_data.password

#     if not empid or not password:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee Code and Password are required")

#     user = users_collection.find_one({"empid": empid})
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Employee Code or Password")

#     if not pwd_context.verify(password, user["password"]):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Employee Code or Password")

#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": empid}, expires_delta=access_token_expires
#     )

#     session_data = {
#         "employeeId": empid,
#         "token": access_token,
#         "created_at": datetime.utcnow(),
#         "expires_at": datetime.utcnow() + access_token_expires
#     }
#     sessions_collection.insert_one(session_data)

#     return {"success": True, "access_token": access_token, "token_type": "bearer", "employeeId": empid, "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60}

# @app.post("/verify_session")
# async def verify_session(token: str = Depends(oauth2_scheme)):
#     employee_id = await get_current_user(token)
#     session = sessions_collection.find_one({"token": token, "employeeId": employee_id})
#     if not session or session["expires_at"] < datetime.utcnow():
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")
#     return {"message": "Session valid"}

# @app.post("/logout")
# async def logout(token: str = Depends(oauth2_scheme)):
#     sessions_collection.delete_one({"token": token})
#     return {"message": "Logged out successfully"}

# @app.get("/employees")
# async def get_employees(current_user: str = Depends(get_current_user)):
#     employees = list(employee_details_collection.find({}, {"_id": 0}))
#     return employees

# @app.get("/clients")
# async def get_clients(current_user: str = Depends(get_current_user)):
#     clients = list(client_details_collection.find({}, {"_id": 0}))
#     return clients

# @app.post("/save_timesheets")
# async def save_timesheets(entries: List[TimesheetEntry], current_user: str = Depends(get_current_user)):
#     print("Received timesheets:", entries)
#     collection = timesheets_collection

#     if not entries:
#         print("No timesheets to save.")
#         return {"message": "No data to save", "success": False}

#     # Validate that employeeId matches the authenticated user
#     for entry in entries:
#         if entry.employeeId != current_user:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized employee ID")

#     employee_data = {}
#     now_iso = datetime.utcnow().isoformat()
    
#     for timesheet in entries:
#         employee_id = timesheet.employeeId
#         week_period = timesheet.weekPeriod or "No Week"

#         if employee_id not in employee_data:
#             employee_data[employee_id] = {
#                 "employeeId": timesheet.employeeId,
#                 "employeeName": timesheet.employeeName or "",
#                 "designation": timesheet.designation or "",
#                 "gender": timesheet.gender or "",
#                 "partner": timesheet.partner or "",
#                 "reportingManager": timesheet.reportingManager or "",
#                 "department": timesheet.department or "",
#                 "Data": [],
#                 "hits": timesheet.hits or "",
#                 "misses": timesheet.misses or "",
#                 "feedback_hr": timesheet.feedback_hr or "",
#                 "feedback_it": timesheet.feedback_it or "",
#                 "feedback_crm": timesheet.feedback_crm or "",
#                 "feedback_others": timesheet.feedback_others or "",
#                 "created_time": now_iso,
#                 "updated_time": now_iso
#             }
            

#         daily_entry = {
#             "date": timesheet.date or "",
#             "location": timesheet.location or "",
#             "projectStartTime": timesheet.projectStartTime or "",
#             "projectEndTime": timesheet.projectEndTime or "",
#             "punchIn": timesheet.punchIn or "",
#             "punchOut": timesheet.punchOut or "",
#             "client": timesheet.client or "",
#             "project": timesheet.project or "",
#             "projectCode": timesheet.projectCode or "",
#             "reportingManagerEntry": timesheet.reportingManagerEntry or "",
#             "activity": timesheet.activity or "",
#             "hours": timesheet.hours or "",
#             "billable": timesheet.billable or "",
#             "remarks": timesheet.remarks or "",
#             "id": str(ObjectId()),
#             "created_time": now_iso,
#             "updated_time": now_iso
#         }

#         # Find or create the week entry in employee_data
#         week_found = False
#         for week_obj in employee_data[employee_id]["Data"]:
#             if week_period in week_obj:
#                 week_obj[week_period].append(daily_entry)
#                 week_found = True
#                 break
#         if not week_found:
#             employee_data[employee_id]["Data"].append({week_period: [daily_entry]})

#     print("Processing and saving data to DB...")
#     for employee_id, data in employee_data.items():
#         existing_doc = collection.find_one({"employeeId": employee_id})
#         if existing_doc:
#             print(f"Updating existing document for employeeId: {employee_id}")
#             existing_data = existing_doc.get("Data", [])
            
#             # Merge new data with existing data
#             new_data = data["Data"]
#             for new_week_obj in new_data:
#                 week = list(new_week_obj.keys())[0]
#                 week_entries = new_week_obj[week]
                
#                 # Find if the week exists in existing_data
#                 week_found = False
#                 for existing_week_obj in existing_data:
#                     if week in existing_week_obj:
#                         existing_week_obj[week].extend(week_entries)
#                         week_found = True
#                         break
#                 if not week_found:
#                     existing_data.append(new_week_obj)
            
#             # Recalculate totals from all entries
#             total_hours = 0
#             total_billable_hours = 0
#             total_non_billable_hours = 0
#             for week_obj in existing_data:
#                 for week, entries in week_obj.items():
#                     for entry in entries:
#                         try:
#                             hours = float(entry['hours'] or 0)
#                         except ValueError:
#                             hours = 0
#                         total_hours += hours
#                         if entry.get('billable') == "Yes":
#                             total_billable_hours += hours
#                         elif entry.get('billable') == "No":
#                             total_non_billable_hours += hours

#             # Update the document
#             result = collection.update_one(
#                 {"employeeId": employee_id},
#                 {"$set": {
#                     "Data": existing_data,
#                     "employeeName": data["employeeName"],
#                     "designation": data["designation"],
#                     "gender": data["gender"],
#                     "partner": data["partner"],
#                     "reportingManager": data["reportingManager"],
#                     "department": data["department"],
#                     "updated_time": now_iso,
#                     "hits": data["hits"] or "",
#                     "misses": data["misses"] or "",
#                     "feedback_hr": data["feedback_hr"] or "",
#                     "feedback_it": data["feedback_it"] or "",
#                     "feedback_crm": data["feedback_crm"] or "",
#                     "feedback_others": data["feedback_others"] or "",
#                     "totalHours": total_hours,
#                     "totalBillableHours": total_billable_hours,
#                     "totalNonBillableHours": total_non_billable_hours
#                 }}
#             )
#             print(f"Updated {result.modified_count} document(s)")
#         else:
#             print(f"Inserting new document for employeeId: {employee_id}")
#             # Calculate totals for new document
#             total_hours = 0
#             total_billable_hours = 0
#             total_non_billable_hours = 0
#             for week_obj in data["Data"]:
#                 for week, entries in week_obj.items():
#                     for entry in entries:
#                         try:
#                             hours = float(entry['hours'] or 0)
#                         except ValueError:
#                             hours = 0
#                         total_hours += hours
#                         if entry.get('billable') == "Yes":
#                             total_billable_hours += hours
#                         elif entry.get('billable') == "No":
#                             total_non_billable_hours += hours

#             data["totalHours"] = total_hours
#             data["totalBillableHours"] = total_billable_hours
#             data["totalNonBillableHours"] = total_non_billable_hours
#             data["created_time"] = now_iso
#             result = collection.insert_one(data)
#             print(f"Inserted document with ID: {result.inserted_id}")

#     return {"message": "Timesheets saved successfully", "employee_ids": list(employee_data.keys()), "success": True}

# @app.get("/timesheets/{employee_id}")
# async def get_timesheets(employee_id: str, current_user: str = Depends(get_current_user)):
#     if employee_id != current_user:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access")
    
#     try:
#         doc = timesheets_collection.find_one({"employeeId": employee_id})
#         if not doc:
#             print(f"No document found for employeeId: {employee_id}")
#             return {"success": True, "Data": [], "totalHours": 0, "totalBillableHours": 0, "totalNonBillableHours": 0}
        
#         # Flatten the nested structure for frontend
#         flattened_data = []
        
#         # Get top-level employee info
#         employee_info = {
#             "employeeId": doc.get("employeeId", ""),
#             "employeeName": doc.get("employeeName", ""),
#             "designation": doc.get("designation", ""),
#             "gender": doc.get("gender", ""),
#             "partner": doc.get("partner", ""),
#             "reportingManager": doc.get("reportingManager", ""),
#             "department": doc.get("department", ""),
#             "hits": doc.get("hits", ""),
#             "misses": doc.get("misses", ""),
#             "feedback_hr": doc.get("feedback_hr", ""),
#             "feedback_it": doc.get("feedback_it", ""),
#             "feedback_crm": doc.get("feedback_crm", ""),
#             "feedback_others": doc.get("feedback_others", ""),
#             "totalHours": doc.get("totalHours", 0),
#             "totalBillableHours": doc.get("totalBillableHours", 0),
#             "totalNonBillableHours": doc.get("totalNonBillableHours", 0)
#         }
        
#         # Handle Data field as a list of {week: [entries]}
#         existing_data = doc.get("Data", [])
#         print(f"Processing Data for employeeId: {employee_id}, Data: {existing_data}")
        
#         for week_item in existing_data:
#             if isinstance(week_item, dict):
#                 week_period = next(iter(week_item), None)
#                 if week_period:
#                     week_entries = week_item.get(week_period, [])
#                     for entry in week_entries:
#                         if isinstance(entry, dict):
#                             flattened_entry = {**employee_info, **entry}
#                             flattened_entry["weekPeriod"] = week_period
#                             flattened_data.append(flattened_entry)
        
#         print(f"Returning flattened data: {flattened_data}")
#         return {
#             "success": True,
#             "Data": flattened_data,
#             "totalHours": employee_info["totalHours"],
#             "totalBillableHours": employee_info["totalBillableHours"],
#             "totalNonBillableHours": employee_info["totalNonBillableHours"]
#         }
#     except Exception as e:
#         print(f"Error fetching timesheets for employeeId: {employee_id}, Error: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Failed to fetch timesheets: {str(e)}")

# @app.put("/update_timesheet/{employee_id}/{entry_id}")
# async def update_timesheet(employee_id: str, entry_id: str, update_data: UpdateTimesheetRequest, current_user: str = Depends(get_current_user)):
#     print(f"Updating timesheet entry {entry_id} for employee {employee_id} with data: {update_data}")
#     if employee_id != current_user:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access")
    
#     try:
#         now_iso = datetime.utcnow().isoformat()
#         collection = timesheets_collection
        
#         # Find the document
#         doc = collection.find_one({"employeeId": employee_id})
#         if not doc:
#             raise HTTPException(status_code=404, detail="Employee document not found")
        
#         entry_found = False
#         week_found = None
#         updated = False
        
#         # Search through all weeks and entries - Data is a list of {week: [entries]}
#         if "Data" in doc and isinstance(doc["Data"], list):
#             for week_obj in doc["Data"]:
#                 for week_period, week_entries in week_obj.items():
#                     if isinstance(week_entries, list):
#                         for i, entry in enumerate(week_entries):
#                             if entry.get("id") == entry_id:
#                                 # Update this specific entry
#                                 updated_entry = {
#                                     "date": update_data.date or entry.get("date", ""),
#                                     "location": update_data.location or entry.get("location", ""),
#                                     "projectStartTime": update_data.projectStartTime or entry.get("projectStartTime", ""),
#                                     "projectEndTime": update_data.projectEndTime or entry.get("projectEndTime", ""),
#                                     "punchIn": update_data.punchIn or entry.get("punchIn", ""),
#                                     "punchOut": update_data.punchOut or entry.get("punchOut", ""),
#                                     "client": update_data.client or entry.get("client", ""),
#                                     "project": update_data.project or entry.get("project", ""),
#                                     "projectCode": update_data.projectCode or entry.get("projectCode", ""),
#                                     "reportingManagerEntry": update_data.reportingManagerEntry or entry.get("reportingManagerEntry", ""),
#                                     "activity": update_data.activity or entry.get("activity", ""),
#                                     "hours": update_data.hours or entry.get("hours", ""),
#                                     "workingHours": update_data.workingHours or entry.get("workingHours", ""),
#                                     "billable": update_data.billable or entry.get("billable", ""),
#                                     "remarks": update_data.remarks or entry.get("remarks", ""),
#                                     "updated_time": now_iso,
#                                     "id": entry_id  # Keep the same ID
#                                 }
                                
#                                 # Replace the entry in the array
#                                 week_obj[week_period][i] = updated_entry
#                                 updated = True
#                                 entry_found = True
#                                 week_found = week_period
#                                 break
#                     if updated:
#                         break
        
#         if not entry_found:
#             raise HTTPException(status_code=404, detail="Timesheet entry not found")
        
#         # Update the document in database
#         collection.update_one(
#             {"employeeId": employee_id},
#             {"$set": {
#                 "Data": doc["Data"],
#                 "updated_time": now_iso
#             }}
#         )
        
#         return {"success": True, "message": "Timesheet entry updated successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to update timesheet: {str(e)}")

# # Health check endpoint
# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}



from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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
import re
from passlib.context import CryptContext
import hashlib
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__ident="2b", bcrypt__rounds=12)

# Load environment variables
load_dotenv()

app = FastAPI(title="Professional Time Sheet API", version="1.0.0")

# CORS middleware - Update allow_origins for production security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Generate a secure JWT secret key (use environment variable in production)
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# MongoDB connection
MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
if not MONGO_CONNECTION_STRING:
    raise ValueError("MONGO_CONNECTION_STRING environment variable is required")

client = MongoClient(MONGO_CONNECTION_STRING)
db = client["Timesheets"]
timesheets_collection = db["Timesheet_data"]
sessions_collection = db["sessions"]
employee_details_collection = db["Employee_details"]
client_details_collection = db["Client_details"]
users_collection = db["users"]

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

class RegisterRequest(BaseModel):
    empid: str
    password: str

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
    projectHours: Optional[str] = None
    workingHours: Optional[str] = None
    billable: Optional[str] = None
    remarks: Optional[str] = None
    hits: Optional[str] = None
    misses: Optional[str] = None
    feedback_hr: Optional[str] = None
    feedback_it: Optional[str] = None
    feedback_crm: Optional[str] = None
    feedback_others: Optional[str] = None

class LoginRequest(BaseModel):
    empid: str
    password: str

class UpdateTimesheetRequest(BaseModel):
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
    projectHours: Optional[str] = None
    workingHours: Optional[str] = None
    billable: Optional[str] = None
    remarks: Optional[str] = None

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    print(f"Expires delta: {expires_delta}")
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=1440)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        print("No token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        employee_id: str = payload.get("sub")
        print(f"Decoded payload: {payload}")
        if employee_id is None:
            print("No employee_id")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        print(f"Token: {token}, Employee_id: {employee_id}")
        
        session = sessions_collection.find_one({
            "token": token, 
            "employeeId": employee_id,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not session:
            print("No session")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")
            
        return employee_id
    except jwt.PyJWTError:
        print(f"Error decoding token: {token}")
        print("Invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Define frontend path
frontend_path = os.path.join(os.path.dirname(__file__), "static")
print("Frontend path:", frontend_path)
if os.path.exists(frontend_path):
    print("Files in frontend:", os.listdir(frontend_path))
else:
    print(f"Frontend directory not found at: {frontend_path}")

# Mount static files for assets
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/", response_class=FileResponse)
async def read_root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/login", response_class=FileResponse)
async def login_page():
    return FileResponse(os.path.join(frontend_path, "login.html"))

@app.get("/dashboard", response_class=FileResponse)
async def dashboard_page():
    return FileResponse(os.path.join(frontend_path, "index.html"))


@app.post("/register")
async def register(request: RegisterRequest):
    empid = request.empid.strip().upper()
    password = request.password

    if len(password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters")
    if not re.search(r'[A-Z]', password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one lowercase letter")
    if not re.search(r'\d', password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one number")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one special character")

    employee = employee_details_collection.find_one({"EmpID": empid})
    if not employee:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee does not exist")

    existing_user = users_collection.find_one({"empid": empid})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")

    hashed_password = pwd_context.hash(password)
    user_data = {
        "empid": empid,
        "password": hashed_password
    }
    users_collection.insert_one(user_data)

    return {"success": True, "detail": "Registration successful. Please login."}

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    empid = form_data.username.strip().upper()
    password = form_data.password

    if not empid or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee Code and Password are required")

    user = users_collection.find_one({"empid": empid})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Employee Code or Password")

    if not pwd_context.verify(password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Employee Code or Password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": empid}, expires_delta=access_token_expires
    )

    session_data = {
        "employeeId": empid,
        "token": access_token,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + access_token_expires
    }
    sessions_collection.insert_one(session_data)

    return {"success": True, "access_token": access_token, "token_type": "bearer", "employeeId": empid, "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60}

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

# @app.post("/save_timesheets")
# async def save_timesheets(entries: List[TimesheetEntry], current_user: str = Depends(get_current_user)):
#     print("Received timesheets:", entries)
#     collection = timesheets_collection

#     if not entries:
#         print("No timesheets to save.")
#         return {"message": "No data to save", "success": False}

#     # Validate that employeeId matches the authenticated user
#     for entry in entries:
#         if entry.employeeId != current_user:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized employee ID")

#     employee_data = {}
#     now_iso = datetime.utcnow().isoformat()
    
#     for timesheet in entries:
#         employee_id = timesheet.employeeId
#         week_period = timesheet.weekPeriod or "No Week"

#         if employee_id not in employee_data:
#             employee_data[employee_id] = {
#                 "employeeId": timesheet.employeeId,
#                 "employeeName": timesheet.employeeName or "",
#                 "designation": timesheet.designation or "",
#                 "gender": timesheet.gender or "",
#                 "partner": timesheet.partner or "",
#                 "reportingManager": timesheet.reportingManager or "",
#                 "department": timesheet.department or "",
#                 "Data": [],
#                 "hits": timesheet.hits or "",
#                 "misses": timesheet.misses or "",
#                 "feedback_hr": timesheet.feedback_hr or "",
#                 "feedback_it": timesheet.feedback_it or "",
#                 "feedback_crm": timesheet.feedback_crm or "",
#                 "feedback_others": timesheet.feedback_others or "",
#                 "created_time": now_iso,
#                 "updated_time": now_iso
#             }
            

#         daily_entry = {
#             "date": timesheet.date or "",
#             "location": timesheet.location or "",
#             "projectStartTime": timesheet.projectStartTime or "",
#             "projectEndTime": timesheet.projectEndTime or "",
#             "punchIn": timesheet.punchIn or "",
#             "punchOut": timesheet.punchOut or "",
#             "client": timesheet.client or "",
#             "project": timesheet.project or "",
#             "projectCode": timesheet.projectCode or "",
#             "reportingManagerEntry": timesheet.reportingManagerEntry or "",
#             "activity": timesheet.activity or "",
#             "projectHours": timesheet.projectHours or "",
#             "workingHours": timesheet.workingHours or "",
#             "billable": timesheet.billable or "",
#             "remarks": timesheet.remarks or "",
#             "id": str(ObjectId()),
#             "created_time": now_iso,
#             "updated_time": now_iso
#         }

#         # Find or create the week entry in employee_data
#         week_found = False
#         for week_obj in employee_data[employee_id]["Data"]:
#             if week_period in week_obj:
#                 week_obj[week_period].append(daily_entry)
#                 week_found = True
#                 break
#         if not week_found:
#             employee_data[employee_id]["Data"].append({week_period: [daily_entry]})

#     print("Processing and saving data to DB...")
#     for employee_id, data in employee_data.items():
#         existing_doc = collection.find_one({"employeeId": employee_id})
#         if existing_doc:
#             print(f"Updating existing document for employeeId: {employee_id}")
#             existing_data = existing_doc.get("Data", [])
            
#             # Merge new data with existing data
#             new_data = data["Data"]
#             for new_week_obj in new_data:
#                 week = list(new_week_obj.keys())[0]
#                 week_entries = new_week_obj[week]
                
#                 # Find if the week exists in existing_data
#                 week_found = False
#                 for existing_week_obj in existing_data:
#                     if week in existing_week_obj:
#                         existing_week_obj[week].extend(week_entries)
#                         week_found = True
#                         break
#                 if not week_found:
#                     existing_data.append(new_week_obj)
            
#             # Recalculate totals from all entries
#             total_hours = 0
#             total_billable_hours = 0
#             total_non_billable_hours = 0
#             for week_obj in existing_data:
#                 for week, entries in week_obj.items():
#                     for entry in entries:
#                         try:
#                             hours = float(entry['projectHours'] or 0)
#                         except ValueError:
#                             hours = 0
#                         total_hours += hours
#                         if entry.get('billable') == "Yes":
#                             total_billable_hours += hours
#                         elif entry.get('billable') == "No":
#                             total_non_billable_hours += hours

#             # Update the document
#             result = collection.update_one(
#                 {"employeeId": employee_id},
#                 {"$set": {
#                     "Data": existing_data,
#                     "employeeName": data["employeeName"],
#                     "designation": data["designation"],
#                     "gender": data["gender"],
#                     "partner": data["partner"],
#                     "reportingManager": data["reportingManager"],
#                     "department": data["department"],
#                     "updated_time": now_iso,
#                     "hits": data["hits"] or "",
#                     "misses": data["misses"] or "",
#                     "feedback_hr": data["feedback_hr"] or "",
#                     "feedback_it": data["feedback_it"] or "",
#                     "feedback_crm": data["feedback_crm"] or "",
#                     "feedback_others": data["feedback_others"] or "",
#                     "totalHours": total_hours,
#                     "totalBillableHours": total_billable_hours,
#                     "totalNonBillableHours": total_non_billable_hours
#                 }}
#             )
#             print(f"Updated {result.modified_count} document(s)")
#         else:
#             print(f"Inserting new document for employeeId: {employee_id}")
#             # Calculate totals for new document
#             total_hours = 0
#             total_billable_hours = 0
#             total_non_billable_hours = 0
#             for week_obj in data["Data"]:
#                 for week, entries in week_obj.items():
#                     for entry in entries:
#                         try:
#                             hours = float(entry['projectHours'] or 0)
#                         except ValueError:
#                             hours = 0
#                         total_hours += hours
#                         if entry.get('billable') == "Yes":
#                             total_billable_hours += hours
#                         elif entry.get('billable') == "No":
#                             total_non_billable_hours += hours

#             data["totalHours"] = total_hours
#             data["totalBillableHours"] = total_billable_hours
#             data["totalNonBillableHours"] = total_non_billable_hours
#             data["created_time"] = now_iso
#             result = collection.insert_one(data)
#             print(f"Inserted document with ID: {result.inserted_id}")

#     return {"message": "Timesheets saved successfully", "employee_ids": list(employee_data.keys()), "success": True}

def compute_entry_hash(entry: dict) -> str:
    """Compute a unique hash for an entry based on key fields (exclude id, timestamps)."""
    key_fields = {
        "date": entry.get("date", ""),
        "location": entry.get("location", ""),
        "projectStartTime": entry.get("projectStartTime", ""),
        "projectEndTime": entry.get("projectEndTime", ""),
        "punchIn": entry.get("punchIn", ""),
        "punchOut": entry.get("punchOut", ""),
        "client": entry.get("client", ""),
        "project": entry.get("project", ""),
        "projectCode": entry.get("projectCode", ""),
        "reportingManagerEntry": entry.get("reportingManagerEntry", ""),
        "activity": entry.get("activity", ""),
        "projectHours": entry.get("projectHours", ""),
        "workingHours": entry.get("workingHours", ""),
        "billable": entry.get("billable", ""),
        "remarks": entry.get("remarks", "")
    }
    # Sort and JSON dump for consistent hashing
    sorted_fields = json.dumps(key_fields, sort_keys=True)
    return hashlib.sha256(sorted_fields.encode()).hexdigest()

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
        week_period = timesheet.weekPeriod or "No Week"

        if employee_id not in employee_data:
            employee_data[employee_id] = {
                "employeeId": timesheet.employeeId,
                "employeeName": timesheet.employeeName or "",
                "designation": timesheet.designation or "",
                "gender": timesheet.gender or "",
                "partner": timesheet.partner or "",
                "reportingManager": timesheet.reportingManager or "",
                "department": timesheet.department or "",
                "Data": [],
                "hits": timesheet.hits or "",
                "misses": timesheet.misses or "",
                "feedback_hr": timesheet.feedback_hr or "",
                "feedback_it": timesheet.feedback_it or "",
                "feedback_crm": timesheet.feedback_crm or "",
                "feedback_others": timesheet.feedback_others or "",
                "created_time": now_iso,
                "updated_time": now_iso
            }

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
            "projectHours": timesheet.projectHours or "",
            "workingHours": timesheet.workingHours or "",
            "billable": timesheet.billable or "",
            "remarks": timesheet.remarks or "",
            "id": str(ObjectId()),
            "created_time": now_iso,
            "updated_time": now_iso
        }

        # Find or create the week entry in employee_data
        week_found = False
        for week_obj in employee_data[employee_id]["Data"]:
            if week_period in week_obj:
                week_obj[week_period].append(daily_entry)
                week_found = True
                break
        if not week_found:
            employee_data[employee_id]["Data"].append({week_period: [daily_entry]})

    print("Processing and saving data to DB...")
    for employee_id, data in employee_data.items():
        existing_doc = collection.find_one({"employeeId": employee_id})
        if existing_doc:
            print(f"Updating existing document for employeeId: {employee_id}")
            existing_data = existing_doc.get("Data", [])
            
            # Pre-compute hashes for all existing entries (for duplicate check)
            existing_hashes = set()
            for week_obj in existing_data:
                for week, entries in week_obj.items():
                    for entry in entries:
                        existing_hashes.add(compute_entry_hash(entry))
            
            # Merge new data with existing data, skipping duplicates
            new_data = data["Data"]
            skipped_count = 0
            for new_week_obj in new_data:
                week = list(new_week_obj.keys())[0]
                new_week_entries = new_week_obj[week]
                
                # Filter out duplicates from new entries
                filtered_entries = []
                for new_entry in new_week_entries:
                    new_hash = compute_entry_hash(new_entry)
                    if new_hash in existing_hashes:
                        print(f"Skipping duplicate entry for date {new_entry['date']} (hash: {new_hash})")
                        skipped_count += 1
                        continue
                    filtered_entries.append(new_entry)
                    # Add to existing hashes to prevent intra-batch duplicates
                    existing_hashes.add(new_hash)
                
                if not filtered_entries:
                    continue  # Skip empty week
                
                # Find if the week exists in existing_data
                week_found = False
                for existing_week_obj in existing_data:
                    if week in existing_week_obj:
                        existing_week_obj[week].extend(filtered_entries)
                        week_found = True
                        break
                if not week_found:
                    existing_data.append({week: filtered_entries})
            
            # Recalculate totals from all entries
            total_hours = 0
            total_billable_hours = 0
            total_non_billable_hours = 0
            for week_obj in existing_data:
                for week, entries in week_obj.items():
                    for entry in entries:
                        try:
                            hours = float(entry['projectHours'] or 0)
                        except ValueError:
                            hours = 0
                        total_hours += hours
                        if entry.get('billable') == "Yes":
                            total_billable_hours += hours
                        elif entry.get('billable') == "No":
                            total_non_billable_hours += hours

            # Update the document
            result = collection.update_one(
                {"employeeId": employee_id},
                {"$set": {
                    "Data": existing_data,
                    "employeeName": data["employeeName"],
                    "designation": data["designation"],
                    "gender": data["gender"],
                    "partner": data["partner"],
                    "reportingManager": data["reportingManager"],
                    "department": data["department"],
                    "updated_time": now_iso,
                    "hits": data["hits"] or "",
                    "misses": data["misses"] or "",
                    "feedback_hr": data["feedback_hr"] or "",
                    "feedback_it": data["feedback_it"] or "",
                    "feedback_crm": data["feedback_crm"] or "",
                    "feedback_others": data["feedback_others"] or "",
                    "totalHours": total_hours,
                    "totalBillableHours": total_billable_hours,
                    "totalNonBillableHours": total_non_billable_hours
                }}
            )
            print(f"Updated {result.modified_count} document(s). Skipped {skipped_count} duplicates.")
        else:
            print(f"Inserting new document for employeeId: {employee_id}")
            # For new docs, no duplicate check needed (nothing existing)
            # Calculate totals for new document
            total_hours = 0
            total_billable_hours = 0
            total_non_billable_hours = 0
            for week_obj in data["Data"]:
                for week, entries in week_obj.items():
                    for entry in entries:
                        try:
                            hours = float(entry['projectHours'] or 0)
                        except ValueError:
                            hours = 0
                        total_hours += hours
                        if entry.get('billable') == "Yes":
                            total_billable_hours += hours
                        elif entry.get('billable') == "No":
                            total_non_billable_hours += hours

            data["totalHours"] = total_hours
            data["totalBillableHours"] = total_billable_hours
            data["totalNonBillableHours"] = total_non_billable_hours
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
            print(f"No document found for employeeId: {employee_id}")
            return {"success": True, "Data": [], "totalHours": 0, "totalBillableHours": 0, "totalNonBillableHours": 0}
        
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
            "department": doc.get("department", ""),
            "hits": doc.get("hits", ""),
            "misses": doc.get("misses", ""),
            "feedback_hr": doc.get("feedback_hr", ""),
            "feedback_it": doc.get("feedback_it", ""),
            "feedback_crm": doc.get("feedback_crm", ""),
            "feedback_others": doc.get("feedback_others", ""),
            "totalHours": doc.get("totalHours", 0),
            "totalBillableHours": doc.get("totalBillableHours", 0),
            "totalNonBillableHours": doc.get("totalNonBillableHours", 0)
        }
        
        # Handle Data field as a list of {week: [entries]}
        existing_data = doc.get("Data", [])
        print(f"Processing Data for employeeId: {employee_id}, Data: {existing_data}")
        
        for week_item in existing_data:
            if isinstance(week_item, dict):
                week_period = next(iter(week_item), None)
                if week_period:
                    week_entries = week_item.get(week_period, [])
                    for entry in week_entries:
                        if isinstance(entry, dict):
                            flattened_entry = {**employee_info, **entry}
                            flattened_entry["weekPeriod"] = week_period
                            flattened_data.append(flattened_entry)
        
        print(f"Returning flattened data: {flattened_data}")
        return {
            "success": True,
            "Data": flattened_data,
            "totalHours": employee_info["totalHours"],
            "totalBillableHours": employee_info["totalBillableHours"],
            "totalNonBillableHours": employee_info["totalNonBillableHours"]
        }
    except Exception as e:
        print(f"Error fetching timesheets for employeeId: {employee_id}, Error: {str(e)}")
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
        week_found = None
        updated = False
        
        # Search through all weeks and entries - Data is a list of {week: [entries]}
        if "Data" in doc and isinstance(doc["Data"], list):
            for week_obj in doc["Data"]:
                for week_period, week_entries in week_obj.items():
                    if isinstance(week_entries, list):
                        for i, entry in enumerate(week_entries):
                            if entry.get("id") == entry_id:
                                # Update this specific entry
                                updated_entry = {
                                    "date": update_data.date or entry.get("date", ""),
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
                                    "projectHours": update_data.projectHours or entry.get("projectHours", ""),
                                    "workingHours": update_data.workingHours or entry.get("workingHours", ""),
                                    "billable": update_data.billable or entry.get("billable", ""),
                                    "remarks": update_data.remarks or entry.get("remarks", ""),
                                    "updated_time": now_iso,
                                    "id": entry_id  # Keep the same ID
                                }
                                
                                # Replace the entry in the array
                                week_obj[week_period][i] = updated_entry
                                updated = True
                                entry_found = True
                                week_found = week_period
                                break
                    if updated:
                        break
        
        if not entry_found:
            raise HTTPException(status_code=404, detail="Timesheet entry not found")

        # Recalculate totals
        total_hours = 0
        total_billable_hours = 0
        total_non_billable_hours = 0
        for week_obj in doc["Data"]:
            for week, entries in week_obj.items():
                for entry in entries:
                    try:
                        hours = float(entry['projectHours'] or 0)
                    except ValueError:
                        hours = 0
                    total_hours += hours
                    if entry.get('billable') == "Yes":
                        total_billable_hours += hours
                    elif entry.get('billable') == "No":
                        total_non_billable_hours += hours
        
        # Update the document in database
        collection.update_one(
            {"employeeId": employee_id},
            {"$set": {
                "Data": doc["Data"],
                "updated_time": now_iso,
                "totalHours": total_hours,
                "totalBillableHours": total_billable_hours,
                "totalNonBillableHours": total_non_billable_hours
            }}
        )
        
        return {"success": True, "message": "Timesheet entry updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update timesheet: {str(e)}")

@app.delete("/delete_timesheet/{employee_id}/{entry_id}")
async def delete_timesheet(employee_id: str, entry_id: str, current_user: str = Depends(get_current_user)):
    print(f"Deleting timesheet entry {entry_id} for employee {employee_id}")
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
        
        # Search through all weeks and entries
        if "Data" in doc and isinstance(doc["Data"], list):
            new_data = []
            for week_obj in doc["Data"]:
                new_week_obj = {}
                for week_period, week_entries in week_obj.items():
                    if isinstance(week_entries, list):
                        new_entries = [entry for entry in week_entries if entry.get("id") != entry_id]
                        if len(new_entries) != len(week_entries):
                            entry_found = True
                        if new_entries:  # Only add if not empty
                            new_week_obj[week_period] = new_entries
                if new_week_obj:
                    new_data.append(new_week_obj)
            doc["Data"] = new_data
        
        if not entry_found:
            raise HTTPException(status_code=404, detail="Timesheet entry not found")
        
        # Recalculate totals
        total_hours = 0
        total_billable_hours = 0
        total_non_billable_hours = 0
        for week_obj in doc["Data"]:
            for week, entries in week_obj.items():
                for entry in entries:
                    try:
                        hours = float(entry['projectHours'] or 0)
                    except ValueError:
                        hours = 0
                    total_hours += hours
                    if entry.get('billable') == "Yes":
                        total_billable_hours += hours
                    elif entry.get('billable') == "No":
                        total_non_billable_hours += hours
        
        # Update the document
        collection.update_one(
            {"employeeId": employee_id},
            {"$set": {
                "Data": doc["Data"],
                "updated_time": now_iso,
                "totalHours": total_hours,
                "totalBillableHours": total_billable_hours,
                "totalNonBillableHours": total_non_billable_hours
            }}
        )
        
        return {"success": True, "message": "Timesheet entry deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete timesheet: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}