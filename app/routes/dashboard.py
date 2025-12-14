# filename: app/routes/dashboard.py
from flask import render_template, jsonify, send_file
from flask_login import login_required, current_user
from datetime import date, timedelta
from app.routes import dashboard_bp
from app.models import Application
from app.utils import export_applications_to_csv
from io import BytesIO

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    applications = Application.query.filter_by(user_id=current_user.id).all()
    
    # Statistics
    total = len(applications)
    
    # Group by status
    status_counts = {}
    for app in applications:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1
    
    # Group by type
    type_counts = {}
    for app in applications:
        type_counts[app.application_type] = type_counts.get(app.application_type, 0) + 1
    
    # Upcoming deadlines
    today = date.today()
    upcoming_7 = []
    upcoming_14 = []
    upcoming_30 = []
    overdue = []
    
    for app in applications:
        if app.deadline:
            days = (app.deadline - today).days
            if days < 0:
                overdue.append(app)
            elif 0 <= days <= 7:
                upcoming_7.append(app)
            elif 8 <= days <= 14:
                upcoming_14.append(app)
            elif 15 <= days <= 30:
                upcoming_30.append(app)
    
    # Sort by urgency
    overdue.sort(key=lambda x: x.deadline)
    upcoming_7.sort(key=lambda x: x.deadline)
    upcoming_14.sort(key=lambda x: x.deadline)
    upcoming_30.sort(key=lambda x: x.deadline)
    
    return render_template('dashboard.html',
                         total=total,
                         status_counts=status_counts,
                         type_counts=type_counts,
                         overdue=overdue,
                         upcoming_7=upcoming_7,
                         upcoming_14=upcoming_14,
                         upcoming_30=upcoming_30)

@dashboard_bp.route('/export/csv')
@login_required
def export_csv():
    applications = Application.query.filter_by(user_id=current_user.id).all()
    csv_data = export_applications_to_csv(applications)
    
    # Create in-memory file
    mem = BytesIO()
    mem.write(csv_data.encode('utf-8'))
    mem.seek(0)
    
    filename = f'applications_export_{date.today()}.csv'
    return send_file(mem,
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=filename)

@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    applications = Application.query.filter_by(user_id=current_user.id).all()
    
    status_counts = {}
    type_counts = {}
    
    for app in applications:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1
        type_counts[app.application_type] = type_counts.get(app.application_type, 0) + 1
    
    return jsonify({
        'total': len(applications),
        'status_counts': status_counts,
        'type_counts': type_counts
    })