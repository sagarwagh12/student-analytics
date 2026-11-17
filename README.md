# Real-Time Cloud-Based Student Performance Analytics Dashboard

A beginner-friendly starter project based on the college synopsis and architecture supplied by the student.

## What is included
- Browser dashboard with KPI cards, charts, student records and a live-refresh feed
- Python FastAPI backend
- SQLite database for local development
- Add student marks and attendance records
- CSV sample data and import script
- AWS deployment planning notes for the architecture in the synopsis

## Important architecture note
Your submitted synopsis lists alternatives and optional services: Amazon RDS **or** DynamoDB; AWS Glue **or** Amazon EMR. This starter uses SQLite locally so it can run on a laptop without an AWS bill. It does not pretend that Kinesis, Glue/EMR, Redshift, EC2 or QuickSight are already deployed. The `docs/AWS_DEPLOYMENT_GUIDE.md` explains how to move from the local demo toward the submitted AWS architecture.

## 1. Requirements
- Windows 10/11
- Python 3.10 or newer
- Google Chrome / Edge
- Internet connection for the Chart.js chart library (loaded from CDN)

## 2. Run on Windows
1. Extract this ZIP.
2. Open the extracted folder.
3. Open Command Prompt or VS Code terminal in this folder.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```

5. Install packages:

   ```powershell
   py -m pip install -r backend\requirements.txt
   ```

6. Start the backend:

   ```powershell
   py -m uvicorn backend.main:app --reload
   ```

7. Open this address in Chrome:

   `http://127.0.0.1:8000`

API documentation: `http://127.0.0.1:8000/docs`

## Demo login
- Teacher: `teacher` / `Teacher123`
- Admin: `admin` / `Admin123`

These are demonstration credentials only. Do not use them in a real deployment.

## 3. Load sample records
The app creates the database automatically on first run. To load the sample CSV, open a second terminal in the project folder, activate `.venv`, then run:

```powershell
py backend\import_csv.py
```

## 4. Project folders
- `backend/main.py` - API, demo login, database operations and analytics
- `backend/import_csv.py` - imports sample CSV
- `frontend/index.html` - dashboard user interface
- `frontend/app.js` - browser-side logic and charts
- `frontend/styles.css` - dashboard styling
- `data/sample_students.csv` - sample student information
- `data/sample_records.csv` - sample marks and attendance
- `docs/` - architecture mapping, deployment plan and testing checklist

## 5. What works locally
- Demo teacher/admin login
- View student list
- Add marks and attendance record
- Calculate average marks, attendance percentage and pass percentage
- Charts and recent record feed
- Automatic refresh of dashboard data every 5 seconds (near-real-time demo)

## 6. Before college submission
Replace demo data with approved sample data, change demo credentials, test all features, and capture screenshots. Explain that local SQLite is used for development; the AWS version requires configuring the AWS services described in your synopsis.
