# CodeAlpha Project Management Tool — TaskFlow

A Django full-stack implementation of CodeAlpha Task 3: a collaborative project management tool similar to Trello/Asana.

## Features
- User registration and login/logout
- Project creation and project boards
- Add/assign tasks to project members
- To Do / In Progress / Done workflow
- Task priorities and due dates
- Edit and delete tasks
- Comments and communication within tasks
- Dashboard statistics
- SQLite database
- Django Admin for users, projects, tasks and comments
- Responsive, beginner-friendly UI

## Quick start — Windows CMD
```cmd
cd "C:\path\to\CodeAlpha_ProjectManagement"
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/

## Optional demo data
After migrations, run:
```cmd
python manage.py seed_demo
```
Demo login: `demo` / `Demo@12345`

## Admin
http://127.0.0.1:8000/admin/

## CodeAlpha mapping
Task 3 asks for group projects, task assignment, comments/communication, authentication, project boards and backend management of users/projects/tasks/comments. This project implements those core requirements. The PDF lists real-time notifications/WebSockets only as a bonus, so they are not required for the core task.


## UI refresh
This package includes a teal/navy responsive UI refresh in `static/css/style.css`. The base template uses a versioned stylesheet URL to reduce stale browser-cache issues. Existing Django views, models, routes, and templates are retained.
