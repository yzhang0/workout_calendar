import sqlite3
from datetime import datetime, timedelta
import os

# Get the database path
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'workout_calendar.db')

def get_db():
    # Using SQLite3 instead of SQLAlchemy because I'm not using Flask
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def print_workout(workout):
    # Convert SQLite integers to boolean strings
    completed = "Yes" if workout['completed'] == 1 else "No"
    is_recurring = "Yes" if workout['is_recurring'] == 1 else "No"
    
    print(f"""
    ID: {workout['id']}
    Type: {workout['type']}
    Description: {workout['description'] or 'None'}
    Date: {workout['date']}
    Duration: {workout['duration']} minutes
    Completed: {completed}
    Is Recurring: {is_recurring}
    Recurrence Rule: {workout['recurrence_rule'] or 'None'}
    Recurrence End: {workout['recurrence_end'] or 'None'}
    User ID: {workout['user_id']}
    Created At: {workout['created_at']}
    """)

def view_all_workouts():
    print("\n=== All Workouts ===")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workout")
    workouts = cursor.fetchall()
    if not workouts:
        print("No workouts found in the database.")
    for w in workouts:
        print_workout(w)
    conn.close()

def view_workouts_by_user(user_id):
    print(f"\n=== Workouts for User {user_id} ===")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workout WHERE user_id = ?", (user_id,))
    workouts = cursor.fetchall()
    if not workouts:
        print(f"No workouts found for user {user_id}")
    for w in workouts:
        print_workout(w)
    conn.close()

def view_workouts_by_type(workout_type):
    print(f"\n=== Workouts of type '{workout_type}' ===")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workout WHERE type = ?", (workout_type,))
    workouts = cursor.fetchall()
    if not workouts:
        print(f"No workouts found of type '{workout_type}'")
    for w in workouts:
        print_workout(w)
    conn.close()

def view_recent_workouts(days=7):
    print(f"\n=== Workouts in the last {days} days ===")
    conn = get_db()
    cursor = conn.cursor()
    since_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
    cursor.execute("SELECT * FROM workout WHERE date >= ?", (since_date,))
    workouts = cursor.fetchall()
    if not workouts:
        print(f"No workouts found in the last {days} days")
    for w in workouts:
        print_workout(w)
    conn.close()

def view_completed_workouts():
    print("\n=== Completed Workouts ===")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workout WHERE completed = 1")
    workouts = cursor.fetchall()
    if not workouts:
        print("No completed workouts found")
    for w in workouts:
        print_workout(w)
    conn.close()

def view_users():
    print("\n=== All Users ===")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    if not users:
        print("No users found in the database")
    for user in users:
        print(f"""
    ID: {user['id']}
    Username: {user['username']}
    Email: {user['email']}
        """)
    conn.close()

if __name__ == "__main__":
    print(f"Using database: {db_path}")
    try:
        while True:
            print("\nDatabase Inspection Menu:")
            print("1. View all workouts")
            print("2. View workouts by user ID")
            print("3. View workouts by type")
            print("4. View recent workouts")
            print("5. View completed workouts")
            print("6. View all users")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-6): ")
            
            if choice == "0":
                break
            elif choice == "1":
                view_all_workouts()
            elif choice == "2":
                try:
                    user_id = input("Enter user ID: ")
                    view_workouts_by_user(int(user_id))
                except ValueError:
                    print("Please enter a valid numeric user ID")
            elif choice == "3":
                workout_type = input("Enter workout type: ")
                view_workouts_by_type(workout_type)
            elif choice == "4":
                try:
                    days = input("Enter number of days (default 7): ") or "7"
                    view_recent_workouts(int(days))
                except ValueError:
                    print("Please enter a valid number of days")
            elif choice == "5":
                view_completed_workouts()
            elif choice == "6":
                view_users()
            else:
                print("Invalid choice. Please try again.")
    except KeyboardInterrupt:
        print("\nExiting the program...")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
    finally:
        print("\nGoodbye!")