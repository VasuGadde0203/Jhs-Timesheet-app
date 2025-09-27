# Timesheet Management System

A web-based Timesheet Management System built to track employee work hours, projects, and activities efficiently. This application allows users to input their timesheet data, manage multiple week periods, and export the data to Excel or save it to a MongoDB database via a FastAPI backend.

## Features

- **Employee Information Management**: Input and store static employee details (ID, name, designation, gender, partner, reporting manager, department).
- **Timesheet Tracking**: Add and manage timesheet entries for multiple week periods with daily details (date, location, start/end times, punch in/out, client, project, etc.).
- **Dynamic Week Periods**: Add or delete week sections dynamically to organize timesheet data.
- **Data Validation**: Validate hours (max 16 hours/day) and dates (within last 30 days to next 7 days).
- **Export Functionality**: Export timesheet data to Excel format.
- **Backend Integration**: Save timesheet data to MongoDB using a FastAPI backend.
- **Responsive Design**: Fully responsive interface for desktop and mobile devices.
- **Modal Interface**: Edit timesheet entries using a detailed modal form.

## Prerequisites

- **Frontend**:
  - A modern web browser (Chrome, Firefox, Edge, etc.).
  - Internet connection for loading external libraries (Font Awesome, XLSX).

- **Backend**:
  - Python 3.8+
  - FastAPI
  - pymongo
  - MongoDB (local or Atlas)

- **Development Tools** (optional):
  - Git for version control.
  - Node.js and npm (for potential future enhancements).
  - Text editor (VS Code, Sublime Text, etc.).

## Installation

### 1. Clone the Repository

  git clone https://github.com/your-username/timesheet-management.git
  cd timesheet-management

### 2. Backend Setup

- Install Python dependencies:
  ```bash
  pip install fastapi uvicorn pymongo
- Set up MongoDB:
  - Install MongoDB locally or use MongoDB Atlas.
  - Update the MONGO_URI in the backend code (main.py or equivalent) with your MongoDB connection string.
- Run the FastAPI server:
  ```bash
  - uvicorn main:app --reload --host 0.0.0.0 --port 8000

### 3. Frontend Setup
- No additional installation is required for the frontend as it is a static HTML file with embedded JavaScript and CSS.
- Open index.html in a web browser or serve it using a local server (e.g., python -m http.server).

### 4. Configuration
- Update the API_URL constant in the JavaScript code to match your FastAPI server URL (e.g., http://localhost:8000).

## Usage
**Enter Employee Details:**
- Input the Employee ID to auto-populate name, designation, gender, partner, and reporting manager (if data exists in the backend).
- Manually adjust or fill other fields (department, etc.).
**Add Week Periods:**
- Click "+ Add Week Period" to create a new section for a week.
- Each section includes a table for daily entries.
**Add Timesheet Entries:**
- Click "+ Add New Entry" within a week section to add a row.
- Fill in details like date, location, times, client, project, etc.
- Use the eye icon to edit entries via a modal form.
**Save Data:**
- Click the "Save" button to send the timesheet data to the MongoDB database via the backend.
**Export Data:**
- Click "Export to Excel" to download the timesheet data as an Excel file.

## API Endpoints
- **GET /employees:** Fetch employee details from the database.
- **GET /clients:** Fetch client/project data (if implemented in the backend).
- **POST /save_timesheets:** Save timesheet data to MongoDB.

## Future Updates
- **Dynamic Mails to TLs:** Implement automated email notifications to Team Leads (TLs) for timesheet submissions or approvals.
- **More Modified UI:** Enhance the user interface with modern design elements, improved layouts, and better usability.
- **And Many More:** Plan to add features like user authentication, advanced reporting, multi-user support, and integration with other tools.

## Contributing
1. Fork the repository.
2. Create a new branch
```bash
(git checkout -b feature-branch).
3. Make your changes and commit them
```bash
(git commit -m "Description of changes").
4. Push to the branch
```bash
(git push origin feature-branch).
5. Open a Pull Request.

