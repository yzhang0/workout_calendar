from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app import db
from app.models import User, Workout
from datetime import datetime, timedelta
from dateutil.rrule import rrulestr
from sqlalchemy.exc import IntegrityError
import traceback

bp = Blueprint('main', __name__)

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
    return jsonify([{
        'id': w.id,
        'start': w.date.isoformat(),
        'type': w.type,
        'description': w.description,
        'duration': w.duration,
        'completed': w.completed,
        'className': f"{w.type} {'completed' if w.completed else ''}"
    } for w in workouts])

@bp.route('/api/workouts', methods=['POST'])
@login_required
def create_workout():
    try:
        data = request.json
        print(data)
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        workout = Workout(
            type=data['type'],
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
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()  # This will print the full stack trace to your server log
        return jsonify({'error': str(e)}), 400

@bp.route('/api/workouts/<int:id>', methods=['DELETE'])
@login_required
def delete_workout(id):
    workout = Workout.query.get_or_404(id)
    if workout.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(workout)
    db.session.commit()
    return '', 204

@bp.route('/api/workouts/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_workout(id):
    workout = Workout.query.get_or_404(id)
    if workout.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    workout.completed = not workout.completed
    db.session.commit()
    return jsonify(workout.to_dict())