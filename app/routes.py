from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app import db
from app.models import User, Workout, Goal
from datetime import datetime, timedelta
from dateutil.rrule import rrulestr
from sqlalchemy.exc import IntegrityError
import traceback
from functools import wraps

bp = Blueprint('main', __name__)

def api_wrapper(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    return wrapped

@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.calendar'))
    return render_template('index.html')

@bp.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            # Check if username already exists before trying to create
            existing_user = User.query.filter_by(username=request.form['username']).first()
            if existing_user:
                flash('Username already taken. Please choose a different username.', 'danger')
                return render_template('register.html')
            
            # Check if email already exists
            existing_email = User.query.filter_by(email=request.form['email']).first()
            if existing_email:
                flash('Email already registered. Please use a different email.', 'danger')
                return render_template('register.html')
            
            user = User(username=request.form['username'], email=request.form['email'])
            user.set_password(request.form['password'])
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('main.login'))
            
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            return render_template('register.html')
        except KeyError:
            flash('Please fill in all fields.', 'danger')
            return render_template('register.html')
    
    # If GET request, just render the registration form
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('main.login'))
        
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# API Routes
@bp.route('/api/workouts', methods=['GET'])
@login_required
def get_workouts():
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    events = []
    
    for workout in workouts:
        # Base event data
        event_data = {
            'id': workout.id,
            'title': workout.title,
            'type': workout.type,
            'description': workout.description,
            'duration': workout.duration,
            'completed': workout.completed,
            'className': f"{workout.type} {'completed' if workout.completed else ''}"
        }
        
        if workout.is_recurring and workout.recurrence_rule:
            # Add recurring class to className
            event_data['className'] += ' recurring'
            
            # Parse the recurrence rule
            rule = rrulestr(workout.recurrence_rule, dtstart=workout.date)
            
            # If there's an end date, use it
            if workout.recurrence_end:
                occurrences = rule.between(workout.date, workout.recurrence_end, inc=True)
            else:
                # If no end date, generate next few occurrences
                occurrences = list(rule.xafter(workout.date, count=10, inc=True))
            
            # Create an event for each occurrence
            for occurrence in occurrences:
                occurrence_data = event_data.copy()
                occurrence_data['start'] = occurrence.isoformat()
                events.append(occurrence_data)
        else:
            # Single event
            event_data['start'] = workout.date.isoformat()
            events.append(event_data)
    
    return jsonify(events)

@bp.route('/api/workouts', methods=['POST'])
@login_required
@api_wrapper
def create_workout():
    data = request.json
    workout = Workout(
        type=data['type'],
        title=data['title'],
        date=datetime.fromisoformat(data['date']),
        duration=data['duration'],
        description=data.get('description', ''),
        user_id=current_user.id,
        is_recurring=data.get('is_recurring', False),
        recurrence_rule=data.get('recurrence_rule'),
        recurrence_end=datetime.fromisoformat(data['recurrence_end']) if data.get('recurrence_end') else None
    )
    db.session.add(workout)
    db.session.commit()
    return jsonify(workout.to_dict())

@bp.route('/api/workouts/<int:id>', methods=['DELETE'])
@login_required
@api_wrapper
def delete_workout(id):
    workout = Workout.query.get_or_404(id)
    if workout.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(workout)
    db.session.commit()
    return '', 204

@bp.route('/api/workouts/<int:id>/toggle', methods=['POST'])
@login_required
@api_wrapper
def toggle_workout(id):
    workout = Workout.query.get_or_404(id)
    if workout.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    workout.completed = not workout.completed
    db.session.commit()
    return jsonify(workout.to_dict())

@bp.route('/goals')
@login_required
@api_wrapper
def goals():
    return render_template('goals.html')

@bp.route('/api/goals', methods=['POST'])
@login_required
@api_wrapper
def create_goal():
    data = request.get_json()
    workout_type = data.get('workoutType')
    description = data.get('goalDescription')
    weeks_to_complete = data.get('weeksToWork')
    print(workout_type, description, weeks_to_complete)
    if not (workout_type and description and weeks_to_complete):
        return jsonify({'error': 'Missing required fields'}), 400
    goal = Goal(
        workout_type=workout_type,
        description=description,
        weeks_to_complete=int(weeks_to_complete),
        user_id=current_user.id
    )
    db.session.add(goal)
    db.session.commit()
    print(goal)
    return jsonify({'message': 'Goal created', 'goal': {
        'id': goal.id,
        'workout_type': goal.workout_type,
        'description': goal.description,
        'weeks_to_complete': goal.weeks_to_complete
    }})

@bp.route('/api/goals', methods=['GET'])
@login_required
@api_wrapper
def get_goals():
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': goal.id,
        'workout_type': goal.workout_type,
        'description': goal.description,
        'weeks_to_complete': goal.weeks_to_complete
    } for goal in goals])