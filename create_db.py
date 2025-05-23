from app import create_app, db
from app.models import User, Workout
import traceback

app = create_app('development')
with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database initialized successfully!") 