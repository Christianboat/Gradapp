import logging
from datetime import datetime, timedelta
from flask import current_app
from app import db
from app.models import Application, User, Task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email_reminder(user, subject, body):
    """
    Mock email sender for development.
    In production, this would use Flask-Mail or an external service.
    """
    # Simulate sending email by logging to console
    print("\n" + "="*50)
    print(f"📧 EMAIL SIMULATION TO: {user.email}")
    print(f"SUBJECT: {subject}")
    print("-" * 50)
    print(body)
    print("="*50 + "\n")
    
    # In a real app, you would do:
    # msg = Message(subject, recipients=[user.email], body=body)
    # mail.send(msg)

def check_upcoming_deadlines(app):
    """
    Checks for applications with deadlines in 7 days, 3 days, and 1 day.
    """
    with app.app_context():
        logger.info("Checking for upcoming deadlines...")
        today = datetime.utcnow().date()
        
        # Deadlines to check: 7 days, 3 days, 1 day
        intervals = [7, 3, 1]
        
        for days in intervals:
            target_date = today + timedelta(days=days)
            
            # Find applications due on this target date
            applications = Application.query.filter(
                Application.deadline == target_date,
                Application.status.notin_(['Submitted', 'Accepted', 'Rejected', 'Waitlisted'])
            ).all()
            
            for application in applications:
                user = User.query.get(application.user_id)
                subject = f"Reminder: {application.title} due in {days} day{'s' if days > 1 else ''}!"
                body = f"""Hello {user.username},
                
This is a reminder that your application for '{application.title}' at {application.institution} is due in {days} days on {application.deadline.strftime('%B %d, %Y')}.

Current Status: {application.status}

Don't forget to review your materials and submit on time!

Good luck,
AppTrack Pro Bot
"""
                send_email_reminder(user, subject, body)

def check_overdue_tasks(app):
    """
    Checks for pending tasks created more than 7 days ago (simple heuristic).
    """
    with app.app_context():
        logger.info("Checking for stale tasks...")
        # Logic for task reminders could be added here
        pass
