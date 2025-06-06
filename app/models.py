from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from dateutil.rrule import rrulestr
import json
from app import db, login_manager

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    timezone = db.Column(db.String(50), nullable=False, default='America/Los_Angeles')
    workouts = db.relationship('Workout', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Workout(db.Model):
    # Workout model for tracking exercise sessions
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # 'pilates' or 'dance' or 'skate'
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer)  # duration in minutes
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Fields for recurrence
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_rule = db.Column(db.String(200))  # RRULE string
    recurrence_end = db.Column(db.DateTime)  # When the recurrence ends
    parent_id = db.Column(db.Integer, db.ForeignKey('workout.id'))  # For recurring event instances
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'description': self.description,
            'date': self.date.isoformat(),
            'duration': self.duration,
            'completed': self.completed,
            'is_recurring': self.is_recurring,
            'recurrence_rule': self.recurrence_rule,
            'recurrence_end': self.recurrence_end.isoformat() if self.recurrence_end else None
        }

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    workout_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(200))
    weeks_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('goals', lazy=True))
    subgoals = db.relationship('SubGoal', backref='goal', lazy=True, cascade='all, delete-orphan')

class SubGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(200))
    description = db.Column(db.Text, nullable=False)
    weeks_to_complete = db.Column(db.Integer, nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False) 