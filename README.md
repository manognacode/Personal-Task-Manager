# Personal-Task-Manager
A simple web-based Task Manager application that allows users to manage their daily tasks efficiently. This project is built using Python (without frameworks), SQLite, and basic web technologies.

---

##  Features

-  Task CRUD Operations (Create, Read, Update, Delete)
-  Mark task as Complete (status toggle)
-  Filter tasks by status and priority
-  Search tasks by title
-  Sort tasks by due date and priority
-  Form validation (Frontend + Backend)
-  Dashboard with:
  - Total tasks
  - Pending tasks
  - Completed tasks
  - Overdue tasks
-  Data stored in SQLite database

---

## Tech Stack

- **Backend:** Python (HTTPServer, BaseHTTPRequestHandler)
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript, Bootstrap

---

## Project Structure


Task-Manager/
│
├── Backend/
│ ├── server.py
│ ├── models.py
│
├── DB/
│ ├── database.py
│ ├── schema.sql
│
├── Frontend/
│ ├── index.html
│ ├── css/
│ ├── js/
│
├── .env
└── README.md


##  Setup Instructions

### 1️. Clone the Repository

```bash
git clone https://github.com/your-username/personal-task-manager.git
cd personal-task-manager
Install Requirements

No external libraries required. Uses built-in Python modules.

Run the Application
cd Backend
python server.py

2️. Install Requirements

No external libraries required. Uses built-in Python modules.

3️. Run the Application
cd Backend
python server.py

4️. Open in Browser
http://localhost:8000
---> Database
SQLite database is used
Table structure is defined in schema.sql
Tasks Table Fields:
id – Primary Key
title – Task title
description – Task description
due_date – Due date (YYYY-MM-DD)
status – Pending / In Progress / Done
priority – Low / Medium / High
created_at – Timestamp

 API Endpoints
MethodEndpointDescriptionGET/api/tasksGet all tasksGET/api/tasks/{id}Get task by IDPOST/api/tasksCreate new taskPUT/api/tasks/{id}Update taskDELETE/api/tasks/{id}Delete taskPATCH/api/tasks/{id}/statusUpdate task statusGET/api/dashboardGet dashboard stats

---> Validation
Frontend:
Required fields check
Date validation
Length validation
Backend:
Title length (3–100 chars)
Description max 500 chars
Valid date format
Status & priority validation



--->Dashboard
Displays:
Total tasks
Pending tasks
Completed tasks
Overdue tasks



--->Design Approach
Separation of concerns:
Backend handles API logic
Database handles data storage
Frontend handles UI
Reusable functions for database operations
Clean and readable code structure



--->Notes
No external frameworks used
Built using beginner-friendly approach
Focused on clarity and correctness

Author
M.Sai Manogna


