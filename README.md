# Workout Calendar

A Flask-based web application for scheduling and tracking workout practice sessions.

## Features

- User authentication (register/login)
- Interactive calendar interface
- Schedule workout sessions
- Track workout completion
- View workout details
- Edit and delete workouts
- Responsive design for mobile and desktop

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

The application will be available at `http://localhost:5000`

## Usage

1. Register a new account or login with existing credentials
2. Navigate to the calendar view
3. Add new workouts using the form on the left
4. Click on calendar events to view details
5. Mark workouts as completed or delete them as needed

## Technologies Used

- Flask
- SQLAlchemy
- Flask-Login
- FullCalendar.js
- Bootstrap 5
- SQLite 