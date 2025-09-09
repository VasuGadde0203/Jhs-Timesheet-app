# from fastapi import FastAPI, HTTPException, Depends, status, Request, Body
# from fastapi.security import OAuth2PasswordBearer
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import HTMLResponse, FileResponse
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

# # Load environment variables
# load_dotenv()

# app = FastAPI(title="Professional Time Sheet API", version="1.0.0")

# # CORS middleware - Update allow_origins for production security
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, specify your frontend URL: ["https://your-frontend.com"]
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

# # OAuth2 scheme for token-based authentication
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

# # Pydantic models for request/response validation
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
#     weekPeriod: str
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
#     billable: Optional[str] = None
#     remarks: Optional[str] = None
#     hits: Optional[str] = None
#     misses: Optional[str] = None
#     feedback_hr: Optional[str] = None
#     feedback_it: Optional[str] = None
#     feedback_crm: Optional[str] = None
#     feedback_others: Optional[str] = None

# # Function to create JWT token
# def create_access_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# # Function to verify JWT token
# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         employee_id: str = payload.get("sub")
#         if employee_id is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
#         # Verify session in database
#         session = sessions_collection.find_one({
#             "token": token, 
#             "employeeId": employee_id,
#             "expires_at": {"$gt": datetime.utcnow()}
#         })
        
#         if not session:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")
            
#         return employee_id
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# # Static file serving - Mount static directory
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # Serve login.html as the root page
# @app.get("/", response_class=HTMLResponse)
# async def serve_login_page():
#     """Serve the login page as the default route"""
#     try:
#         with open("static/login.html", "r", encoding="utf-8") as file:
#             return HTMLResponse(content=file.read())
#     except FileNotFoundError:
#         # Fallback if static files are not found
#         return HTMLResponse(content="""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <title>Time Sheet - Login</title>
#             <meta charset="UTF-8">
#             <meta name="viewport" content="width=device-width, initial-scale=1.0">
#             <style>
#                 body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f0f0; }
#                 .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
#                 input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
#                 button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
#                 button:hover { background: #0056b3; }
#                 .error { color: red; margin: 10px 0; }
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <h2>Login to Time Sheet</h2>
#                 <form id="loginForm">
#                     <input type="text" id="empid" placeholder="Employee ID" required>
#                     <input type="password" id="password" placeholder="Password" required>
#                     <button type="submit">Login</button>
#                 </form>
#                 <div id="errorMessage" class="error"></div>
#             </div>
#             <script>
#                 document.getElementById('loginForm').addEventListener('submit', async (e) => {
#                     e.preventDefault();
#                     const empid = document.getElementById('empid').value;
#                     const password = document.getElementById('password').value;
#                     const errorDiv = document.getElementById('errorMessage');
                    
#                     try {
#                         const response = await fetch('/login', {
#                             method: 'POST',
#                             headers: { 'Content-Type': 'application/json' },
#                             body: JSON.stringify({ empid, password })
#                         });
#                         const result = await response.json();
                        
#                         if (response.ok && result.success) {
#                             localStorage.setItem('access_token', result.access_token);
#                             localStorage.setItem('loggedInEmployeeId', result.employeeId);
#                             window.location.href = '/dashboard';
#                         } else {
#                             errorDiv.textContent = result.detail || 'Login failed';
#                         }
#                     } catch (error) {
#                         errorDiv.textContent = 'Login error: ' + error.message;
#                     }
#                 });
#             </script>
#         </body>
#         </html>
#         """)

# # Serve dashboard (index.html) for authenticated users
# @app.get("/dashboard", response_class=HTMLResponse)
# async def serve_dashboard_page(request: Request):
#     """Serve the main timesheet dashboard for authenticated users"""
#     try:
#         with open("static/index2.html", "r", encoding="utf-8") as file:
#             return HTMLResponse(content=file.read())
#     except FileNotFoundError:
#         # Fallback dashboard
#         return HTMLResponse(content="""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <title>Time Sheet Dashboard</title>
#             <meta charset="UTF-8">
#             <meta name="viewport" content="width=device-width, initial-scale=1.0">
#             <style>
#                 body { font-family: Arial, sans-serif; margin: 20px; }
#                 .container { max-width: 1200px; margin: 0 auto; }
#                 .header { background: #007bff; color: white; padding: 20px; border-radius: 5px; }
#                 .welcome { font-size: 24px; margin-bottom: 10px; }
#                 .nav { margin: 20px 0; }
#                 .nav button { margin-right: 10px; padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }
#                 .nav button:hover { background: #218838; }
#                 .content { background: #f8f9fa; padding: 20px; border-radius: 5px; }
#                 .logout { position: fixed; top: 20px; right: 20px; padding: 10px 15px; background: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer; }
#                 .logout:hover { background: #c82333; }
#             </style>
#         </head>
#         <body>
#             <button class="logout" onclick="logout()">Logout</button>
#             <div class="container">
#                 <div class="header">
#                     <div class="welcome">Welcome to Time Sheet Dashboard</div>
#                     <div id="employeeInfo"></div>
#                 </div>
#                 <div class="nav">
#                     <button onclick="loadTimesheet()">Timesheet</button>
#                     <button onclick="loadHistory()">History</button>
#                 </div>
#                 <div class="content" id="mainContent">
#                     <h2>Welcome to your Time Sheet Portal</h2>
#                     <p>Loading your timesheet data...</p>
#                 </div>
#             </div>
#             <script>
#                 const API_URL = '';
#                 let currentUser = localStorage.getItem('loggedInEmployeeId');
                
#                 async function loadEmployeeInfo() {
#                     try {
#                         const token = localStorage.getItem('access_token');
#                         const response = await fetch('/employees', {
#                             headers: { 'Authorization': `Bearer ${token}` }
#                         });
#                         const employees = await response.json();
#                         const userEmployee = employees.find(emp => emp.EmpID === currentUser);
#                         if (userEmployee) {
#                             document.getElementById('employeeInfo').innerHTML = 
#                                 `<strong>${userEmployee['Emp Name'] || 'Employee'}</strong> - ${userEmployee['Designation Name'] || 'Position'}`;
#                         }
#                     } catch (error) {
#                         console.error('Error loading employee info:', error);
#                     }
#                 }
                
#                 async function loadTimesheet() {
#                     document.getElementById('mainContent').innerHTML = '<p>Loading timesheet...</p>';
#                     try {
#                         const token = localStorage.getItem('access_token');
#                         const response = await fetch('/timesheets/' + currentUser, {
#                             headers: { 'Authorization': `Bearer ${token}` }
#                         });
#                         const data = await response.json();
#                         // Display timesheet data
#                         document.getElementById('mainContent').innerHTML = '<h2>Timesheet</h2><pre>' + JSON.stringify(data, null, 2) + '</pre>';
#                     } catch (error) {
#                         document.getElementById('mainContent').innerHTML = '<p>Error loading timesheet: ' + error.message + '</p>';
#                     }
#                 }
                
#                 async function loadHistory() {
#                     document.getElementById('mainContent').innerHTML = '<p>Loading history...</p>';
#                     try {
#                         const token = localStorage.getItem('access_token');
#                         const response = await fetch('/timesheets/' + currentUser, {
#                             headers: { 'Authorization': `Bearer ${token}` }
#                         });
#                         const data = await response.json();
#                         // Display history data
#                         document.getElementById('mainContent').innerHTML = '<h2>History</h2><pre>' + JSON.stringify(data, null, 2) + '</pre>';
#                     } catch (error) {
#                         document.getElementById('mainContent').innerHTML = '<p>Error loading history: ' + error.message + '</p>';
#                     }
#                 }
                
#                 function logout() {
#                     localStorage.removeItem('access_token');
#                     localStorage.removeItem('loggedInEmployeeId');
#                     window.location.href = '/';
#                 }
                
#                 // Initialize
#                 if (!currentUser) {
#                     window.location.href = '/';
#                 } else {
#                     loadEmployeeInfo();
#                     loadTimesheet();
#                 }
#             </script>
#         </body>
#         </html>
#         """)

# # API Routes (your existing endpoints remain unchanged)

# @app.post("/login")
# async def login(login_request: LoginRequest):
#     employee = employee_details_collection.find_one({
#         "EmpID": login_request.empid.strip()
#     })
#     if not employee:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Employee ID or Password")
    
#     # Simple password validation - password should match empid (consider using proper password hashing in production)
#     hashed_password = hashlib.sha256(login_request.password.encode()).hexdigest()
#     hashed_empid = hashlib.sha256(login_request.empid.encode()).hexdigest()
#     if hashed_password != hashed_empid:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Employee ID or Password")
    
#     # Generate token
#     access_token = create_access_token(data={"sub": login_request.empid})
    
#     # Store session
#     session_data = {
#         "employeeId": login_request.empid,
#         "token": access_token,
#         "created_at": datetime.utcnow(),
#         "expires_at": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     }
#     sessions_collection.insert_one(session_data)
    
#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "success": True,
#         "employeeId": login_request.empid
#     }

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
#         week_period = timesheet.weekPeriod

#         if employee_id not in employee_data:
#             employee_data[employee_id] = {
#                 "employeeId": timesheet.employeeId,
#                 "employeeName": timesheet.employeeName or "",
#                 "designation": timesheet.designation or "",
#                 "gender": timesheet.gender or "",
#                 "partner": timesheet.partner or "",
#                 "reportingManager": timesheet.reportingManager or "",
#                 "department": timesheet.department or "",
#                 "Data": {},
#                 "created_time": now_iso if employee_id not in employee_data else employee_data[employee_id].get("created_time"),
#                 "updated_time": now_iso
#             }

#         if week_period not in employee_data[employee_id]["Data"]:
#             employee_data[employee_id]["Data"][week_period] = []

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
#             "hits": timesheet.hits or "",
#             "misses": timesheet.misses or "",
#             "feedback_hr": timesheet.feedback_hr or "",
#             "feedback_it": timesheet.feedback_it or "",
#             "feedback_crm": timesheet.feedback_crm or "",
#             "feedback_others": timesheet.feedback_others or "",
#             "id": str(ObjectId()),  # Unique ID for each entry
#             "created_time": now_iso,
#             "updated_time": now_iso
#         }

#         employee_data[employee_id]["Data"][week_period].append(daily_entry)

#     print("Processing and saving data to DB...")
#     for employee_id, data in employee_data.items():
#         # Convert Data dict to list of {week: entries}
#         week_list = []
#         for week, entries_list in data["Data"].items():
#             week_list.append({week: entries_list})
#         data["Data"] = week_list

#         existing_doc = collection.find_one({"employeeId": employee_id})
#         if existing_doc:
#             print(f"Updating existing document for employeeId: {employee_id}")
#             # Merge Data - existing_doc["Data"] is list of {week: entries}
#             existing_weeks = existing_doc.get("Data", [])
#             new_weeks = data["Data"]
            
#             # For each new week, merge or add
#             for new_week_obj in new_weeks:
#                 week = list(new_week_obj.keys())[0]
#                 found = False
#                 for i, existing_item in enumerate(existing_weeks):
#                     if isinstance(existing_item, dict) and week in existing_item:
#                         existing_weeks[i][week] = new_week_obj[week]
#                         found = True
#                         break
#                 if not found:
#                     existing_weeks.append(new_week_obj)
            
#             # Update the document
#             result = collection.update_one(
#                 {"employeeId": employee_id},
#                 {"$set": {
#                     "Data": existing_weeks,
#                     "employeeName": data["employeeName"],
#                     "designation": data["designation"],
#                     "gender": data["gender"],
#                     "partner": data["partner"],
#                     "reportingManager": data["reportingManager"],
#                     "department": data["department"],
#                     "updated_time": now_iso
#                 }}
#             )
#             print(f"Updated {result.modified_count} document(s)")
#         else:
#             print(f"Inserting new document for employeeId: {employee_id}")
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
#             return {"success": True, "Data": []}
        
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
#             "department": doc.get("department", "")
#         }
        
#         # Iterate through Data structure - now a list of {week: [entries]}
#         if "Data" in doc and isinstance(doc["Data"], list):
#             for week_item in doc["Data"]:
#                 if isinstance(week_item, dict):
#                     week_period = list(week_item.keys())[0]
#                     week_entries = week_item.get(week_period, [])
#                     if isinstance(week_entries, list):
#                         for entry in week_entries:
#                             flattened_entry = {**employee_info, **entry}
#                             flattened_entry["weekPeriod"] = week_period
#                             flattened_data.append(flattened_entry)
        
#         return {"success": True, "Data": flattened_data}
#     except Exception as e:
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
#         updated = False
        
#         # Search through all weeks and entries - Data is list of {week: [entries]}
#         if "Data" in doc and isinstance(doc["Data"], list):
#             for week_item in doc["Data"]:
#                 if isinstance(week_item, dict):
#                     week_period = list(week_item.keys())[0]
#                     week_entries = week_item.get(week_period, [])
#                     if isinstance(week_entries, list):
#                         for i, entry in enumerate(week_entries):
#                             if entry.get("id") == entry_id:
#                                 # Update this specific entry
#                                 updated_entry = {
#                                     "date": update_data.date,
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
#                                     "billable": update_data.billable or entry.get("billable", ""),
#                                     "remarks": update_data.remarks or entry.get("remarks", ""),
#                                     "hits": update_data.hits or entry.get("hits", ""),
#                                     "misses": update_data.misses or entry.get("misses", ""),
#                                     "feedback_hr": update_data.feedback_hr or entry.get("feedback_hr", ""),
#                                     "feedback_it": update_data.feedback_it or entry.get("feedback_it", ""),
#                                     "feedback_crm": update_data.feedback_crm or entry.get("feedback_crm", ""),
#                                     "feedback_others": update_data.feedback_others or entry.get("feedback_others", ""),
#                                     "updated_time": now_iso,
#                                     "id": entry_id  # Keep the same ID
#                                 }
                                
#                                 # Replace the entry in the array
#                                 week_item[week_period][i] = updated_entry
#                                 updated = True
#                                 entry_found = True
#                                 break
#                     if updated:
#                         break
        
#         if not entry_found:
#             raise HTTPException(status_code=404, detail="Timesheet entry not found")
        
#         # Update the document in database - set the whole Data
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


from fastapi import FastAPI, HTTPException, Depends, status, Request, Body
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
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

# Load environment variables
load_dotenv()

app = FastAPI(title="Professional Time Sheet API", version="1.0.0")

# CORS middleware - Update allow_origins for production security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL: ["https://your-frontend.com"]
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

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

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
    hours: Optional[str] = None
    workingHours: Optional[str] = None
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
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        employee_id: str = payload.get("sub")
        if employee_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        # Verify session in database
        session = sessions_collection.find_one({
            "token": token, 
            "employeeId": employee_id,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")
            
        return employee_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Static file serving - Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve login.html as the root page
@app.get("/", response_class=HTMLResponse)
async def serve_login_page():
    """Serve the login page as the default route"""
    try:
        with open("static/login.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        # Fallback if static files are not found
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Time Sheet - Login</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f0f0; }
                .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
                button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
                button:hover { background: #0056b3; }
                .error { color: red; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Login to Time Sheet</h2>
                <form id="loginForm">
                    <input type="text" id="empid" placeholder="Employee ID" required>
                    <input type="password" id="password" placeholder="Password" required>
                    <button type="submit">Login</button>
                </form>
                <div id="errorMessage" class="error"></div>
            </div>
            <script>
                document.getElementById('loginForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const empid = document.getElementById('empid').value;
                    const password = document.getElementById('password').value;
                    const errorDiv = document.getElementById('errorMessage');
                    
                    try {
                        const response = await fetch('/login', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ empid, password })
                        });
                        const result = await response.json();
                        
                        if (response.ok && result.success) {
                            localStorage.setItem('access_token', result.access_token);
                            localStorage.setItem('loggedInEmployeeId', result.employeeId);
                            window.location.href = '/dashboard';
                        } else {
                            errorDiv.textContent = result.detail || 'Login failed';
                        }
                    } catch (error) {
                        errorDiv.textContent = 'Login error: ' + error.message;
                    }
                });
            </script>
        </body>
        </html>
        """)

# Serve dashboard (index.html) for authenticated users
@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard_page(request: Request):
    """Serve the main timesheet dashboard for authenticated users"""
    try:
        with open("static/index2.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        # Fallback dashboard
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Time Sheet Dashboard</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { background: #007bff; color: white; padding: 20px; border-radius: 5px; }
                .welcome { font-size: 24px; margin-bottom: 10px; }
                .nav { margin: 20px 0; }
                .nav button { margin-right: 10px; padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }
                .nav button:hover { background: #218838; }
                .content { background: #f8f9fa; padding: 20px; border-radius: 5px; }
                .logout { position: fixed; top: 20px; right: 20px; padding: 10px 15px; background: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer; }
                .logout:hover { background: #c82333; }
            </style>
        </head>
        <body>
            <button class="logout" onclick="logout()">Logout</button>
            <div class="container">
                <div class="header">
                    <div class="welcome">Welcome to Time Sheet Dashboard</div>
                    <div id="employeeInfo"></div>
                </div>
                <div class="nav">
                    <button onclick="loadTimesheet()">Timesheet</button>
                    <button onclick="loadHistory()">History</button>
                </div>
                <div class="content" id="mainContent">
                    <h2>Welcome to your Time Sheet Portal</h2>
                    <p>Loading your timesheet data...</p>
                </div>
            </div>
            <script>
                const API_URL = '';
                let currentUser = localStorage.getItem('loggedInEmployeeId');
                
                async function loadEmployeeInfo() {
                    try {
                        const token = localStorage.getItem('access_token');
                        const response = await fetch('/employees', {
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        const employees = await response.json();
                        const userEmployee = employees.find(emp => emp.EmpID === currentUser);
                        if (userEmployee) {
                            document.getElementById('employeeInfo').innerHTML = 
                                `<strong>${userEmployee['Emp Name'] || 'Employee'}</strong> - ${userEmployee['Designation Name'] || 'Position'}`;
                        }
                    } catch (error) {
                        console.error('Error loading employee info:', error);
                    }
                }
                
                async function loadTimesheet() {
                    document.getElementById('mainContent').innerHTML = '<p>Loading timesheet...</p>';
                    try {
                        const token = localStorage.getItem('access_token');
                        const response = await fetch('/timesheets/' + currentUser, {
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        const data = await response.json();
                        // Display timesheet data
                        document.getElementById('mainContent').innerHTML = '<h2>Timesheet</h2><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    } catch (error) {
                        document.getElementById('mainContent').innerHTML = '<p>Error loading timesheet: ' + error.message + '</p>';
                    }
                }
                
                async function loadHistory() {
                    document.getElementById('mainContent').innerHTML = '<p>Loading history...</p>';
                    try {
                        const token = localStorage.getItem('access_token');
                        const response = await fetch('/timesheets/' + currentUser, {
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        const data = await response.json();
                        // Display history data
                        document.getElementById('mainContent').innerHTML = '<h2>History</h2><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    } catch (error) {
                        document.getElementById('mainContent').innerHTML = '<p>Error loading history: ' + error.message + '</p>';
                    }
                }
                
                function logout() {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('loggedInEmployeeId');
                    window.location.href = '/';
                }
                
                // Initialize
                if (!currentUser) {
                    window.location.href = '/';
                } else {
                    loadEmployeeInfo();
                    loadTimesheet();
                }
            </script>
        </body>
        </html>
        """)

# API Routes (your existing endpoints remain unchanged)

@app.post("/login")
async def login(login_request: LoginRequest):
    employee = employee_details_collection.find_one({
        "EmpID": login_request.empid.strip()
    })
    if not employee:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Employee ID or Password")
    
    # Simple password validation - password should match empid (consider using proper password hashing in production)
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
    feedback = None
    
    for timesheet in entries:
        employee_id = timesheet.employeeId
        week_period = timesheet.weekPeriod or "No Week"

        if feedback is None and timesheet.hits:
            feedback = {
                "hits": timesheet.hits or "",
                "misses": timesheet.misses or "",
                "feedback_hr": timesheet.feedback_hr or "",
                "feedback_it": timesheet.feedback_it or "",
                "feedback_crm": timesheet.feedback_crm or "",
                "feedback_others": timesheet.feedback_others or ""
            }

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
                "created_time": now_iso,
                "updated_time": now_iso
            }

        if week_period not in employee_data[employee_id]["Data"]:
            employee_data[employee_id]["Data"][week_period] = {
                "entries": [],
                "feedback": feedback or {}
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
            "hours": timesheet.hours or "",
            "workingHours": timesheet.workingHours or "",
            "billable": timesheet.billable or "",
            "remarks": timesheet.remarks or "",
            "id": str(ObjectId()),
            "created_time": now_iso,
            "updated_time": now_iso
        }

        employee_data[employee_id]["Data"][week_period]["entries"].append(daily_entry)

    print("Processing and saving data to DB...")
    for employee_id, data in employee_data.items():
        existing_doc = collection.find_one({"employeeId": employee_id})
        if existing_doc:
            print(f"Updating existing document for employeeId: {employee_id}")
            existing_data = existing_doc.get("Data", {})
            new_data = data["Data"]
            
            for week, week_data in new_data.items():
                if week in existing_data:
                    existing_data[week]["entries"].extend(week_data["entries"])
                    existing_data[week]["feedback"] = week_data["feedback"]
                else:
                    existing_data[week] = week_data
            
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
        
        # Iterate through Data structure - now a dict {week: {"entries": [], "feedback": {}}}
        if "Data" in doc and isinstance(doc["Data"], dict):
            for week_period, week_data in doc["Data"].items():
                week_entries = week_data.get("entries", [])
                feedback = week_data.get("feedback", {})
                for entry in week_entries:
                    flattened_entry = {**employee_info, **entry, **feedback}
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
        week_found = None
        updated = False
        
        # Search through all weeks and entries - Data is dict {week: {"entries": [], "feedback": {}}}
        if "Data" in doc and isinstance(doc["Data"], dict):
            for week_period, week_data in doc["Data"].items():
                week_entries = week_data.get("entries", [])
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
                                "hours": update_data.hours or entry.get("hours", ""),
                                "workingHours": update_data.workingHours or entry.get("workingHours", ""),
                                "billable": update_data.billable or entry.get("billable", ""),
                                "remarks": update_data.remarks or entry.get("remarks", ""),
                                "updated_time": now_iso,
                                "id": entry_id  # Keep the same ID
                            }
                            
                            # Replace the entry in the array
                            doc["Data"][week_period]["entries"][i] = updated_entry
                            updated = True
                            entry_found = True
                            week_found = week_period
                            break
                if updated:
                    break
        
        if not entry_found:
            raise HTTPException(status_code=404, detail="Timesheet entry not found")
        
        # Update the document in database
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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}