import unittest
from datetime import datetime
from app import create_app, db
from app.models import Workout, User

class TestWorkout(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create a test user
        self.test_user = User(username='testuser', email='test@example.com')
        self.test_user.set_password('testpass')
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_workout(self):
        """Test creating a new workout"""
        workout = Workout(
            type='Running',
            title='Morning Run',
            date=datetime.utcnow(),
            duration=30,
            completed=False,
            user_id=self.test_user.id
        )
        db.session.add(workout)
        db.session.commit()

        # Verify the workout was created
        saved_workout = Workout.query.filter_by(title='Morning Run').first()
        self.assertIsNotNone(saved_workout)
        self.assertEqual(saved_workout.type, 'Running')
        self.assertEqual(saved_workout.duration, 30)
        self.assertEqual(saved_workout.user_id, self.test_user.id)

if __name__ == '__main__':
    unittest.main() 