# filename: app/utils.py
from datetime import datetime, date
from flask import url_for
import csv
from io import StringIO

def get_status_color(status):
    color_map = {
        'Not Started': 'secondary',
        'In Progress': 'info',
        'Submitted': 'primary',
        'Interview': 'warning',
        'Offer': 'success',
        'Accepted': 'success',
        'Rejected': 'danger',
        'Waitlisted': 'warning'
    }
    return color_map.get(status, 'secondary')

def get_days_remaining(deadline):
    if not deadline:
        return None
    delta = deadline - date.today()
    return delta.days

def get_urgency_class(days_remaining):
    if days_remaining is None:
        return 'secondary'
    if days_remaining < 0:
        return 'danger'
    elif days_remaining < 3:
        return 'danger'
    elif days_remaining < 7:
        return 'warning'
    elif days_remaining < 14:
        return 'info'
    else:
        return 'success'

def format_date(value, format='%b %d, %Y'):
    if value is None:
        return ''
    if isinstance(value, date):
        return value.strftime(format)
    return value

def export_applications_to_csv(applications):
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Title', 'Type', 'Institution', 'Program/Role', 'Country',
        'Deadline', 'Status', 'Days Remaining', 'Application URL', 'Notes',
        'Created', 'Updated'
    ])
    
    # Write data
    for app in applications:
        writer.writerow([
            app.title,
            app.application_type,
            app.institution,
            app.program_role or '',
            app.country or '',
            app.deadline.strftime('%Y-%m-%d') if app.deadline else '',
            app.status,
            app.days_remaining() or '',
            app.application_url or '',
            app.notes or '',
            app.created_at.strftime('%Y-%m-%d %H:%M'),
            app.updated_at.strftime('%Y-%m-%d %H:%M') if app.updated_at else ''
        ])
    
    return output.getvalue()

def get_upcoming_deadlines(applications, days=7):
    today = date.today()
    end_date = today + timedelta(days=days)
    upcoming = []
    
    for app in applications:
        if app.deadline and today <= app.deadline <= end_date:
            upcoming.append(app)
    
    return sorted(upcoming, key=lambda x: x.deadline)

from datetime import timedelta  # Added for get_upcoming_deadlines function