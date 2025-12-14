# filename: app/routes/applications.py
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from sqlalchemy import or_
from datetime import datetime, date, timedelta
import os
from werkzeug.utils import secure_filename
from app import db
from app.routes import applications_bp
from app.models import Application, Task, Document
from app.forms import ApplicationForm

@applications_bp.route('/')
@login_required
def list():
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    type_filter = request.args.get('type', 'all')
    country_filter = request.args.get('country', 'all')
    search_query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'deadline')
    
    # Base query
    query = Application.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if type_filter != 'all':
        query = query.filter_by(application_type=type_filter)
    
    if country_filter != 'all':
        query = query.filter_by(country=country_filter)
    
    # Apply search
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(or_(
            Application.title.ilike(search),
            Application.institution.ilike(search),
            Application.program_role.ilike(search)
        ))
    
    # Apply sorting
    if sort_by == 'deadline':
        query = query.order_by(Application.deadline.asc())
    elif sort_by == 'created':
        query = query.order_by(Application.created_at.desc())
    elif sort_by == 'status':
        query = query.order_by(Application.status.asc())
    elif sort_by == 'title':
        query = query.order_by(Application.title.asc())
    
    applications = query.all()
    
    return render_template('applications/list.html',
                         applications=applications,
                         current_filters={
                             'status': status_filter,
                             'type': type_filter,
                             'country': country_filter,
                             'search': search_query,
                             'sort': sort_by
                         })

@applications_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ApplicationForm()
    
    if form.validate_on_submit():
        application = Application(
            title=form.title.data,
            application_type=form.application_type.data,
            institution=form.institution.data,
            program_role=form.program_role.data,
            country=form.country.data if form.country.data else None,
            deadline=form.deadline.data,
            status=form.status.data,
            application_url=form.application_url.data,
            notes=form.notes.data,
            user_id=current_user.id
        )
        
        db.session.add(application)
        db.session.commit()
        
        flash('Application created successfully!', 'success')
        return redirect(url_for('applications.view', id=application.id))
    
    # Set default deadline to 30 days from now
    if not form.deadline.data:
        form.deadline.data = date.today() + timedelta(days=30)
    
    return render_template('applications/create.html', form=form)

@applications_bp.route('/<int:id>')
@login_required
def view(id):
    application = Application.query.get_or_404(id)
    
    # Ensure user owns this application
    if application.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('applications.list'))
    
    return render_template('applications/view.html', application=application)

@applications_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    application = Application.query.get_or_404(id)
    
    # Ensure user owns this application
    if application.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('applications.list'))
    
    form = ApplicationForm(obj=application)
    
    if form.validate_on_submit():
        application.title = form.title.data
        application.application_type = form.application_type.data
        application.institution = form.institution.data
        application.program_role = form.program_role.data
        application.country = form.country.data if form.country.data else None
        application.deadline = form.deadline.data
        application.status = form.status.data
        application.application_url = form.application_url.data
        application.notes = form.notes.data
        application.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Application updated successfully!', 'success')
        return redirect(url_for('applications.view', id=application.id))
    
    return render_template('applications/edit.html', form=form, application=application)

@applications_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    application = Application.query.get_or_404(id)
    
    # Ensure user owns this application
    if application.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('applications.list'))
    
    db.session.delete(application)
    db.session.commit()
    
    flash('Application deleted successfully.', 'success')
    return redirect(url_for('applications.list'))

@applications_bp.route('/<int:id>/duplicate', methods=['POST'])
@login_required
def duplicate(id):
    application = Application.query.get_or_404(id)
    
    # Ensure user owns this application
    if application.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('applications.list'))
    
    # Create a copy
    new_application = Application(
        title=f"{application.title} (Copy)",
        application_type=application.application_type,
        institution=application.institution,
        program_role=application.program_role,
        country=application.country,
        deadline=application.deadline,
        status='Not Started',
        application_url=application.application_url,
        notes=application.notes,
        user_id=current_user.id
    )
    
    db.session.add(new_application)
    db.session.commit()
    
    flash('Application duplicated successfully!', 'success')
    return redirect(url_for('applications.edit', id=new_application.id))

@applications_bp.route('/<int:id>/update-status', methods=['POST'])
@login_required
def update_status(id):
    application = Application.query.get_or_404(id)
    
    # Ensure user owns this application
    if application.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    new_status = request.json.get('status')
    if not new_status:
        return jsonify({'error': 'Status required'}), 400
    
    application.status = new_status
    application.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'new_status': new_status,
        'status_color': get_status_color(new_status)
    })

from app.utils import get_status_color

# --- Document Helper Functions ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# --- Document Routes ---
@applications_bp.route('/<int:id>/upload_document', methods=['POST'])
@login_required
def upload_document(id):
    application = Application.query.get_or_404(id)
    if application.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403

    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('applications.view', id=id))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('applications.view', id=id))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Create user specific directory
        user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id))
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
            
        filepath = os.path.join(user_dir, filename)
        file.save(filepath)
        
        # Save to DB
        document = Document(
            filename=filename,
            filepath=os.path.join(str(current_user.id), filename),
            application_id=application.id
        )
        db.session.add(document)
        db.session.commit()
        
        flash('File uploaded successfully', 'success')
    else:
        flash('File type not allowed', 'danger')
        
    return redirect(url_for('applications.view', id=id))

@applications_bp.route('/document/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    if document.application.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
        
    try:
        # Remove file from system
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.filepath)
        if os.path.exists(full_path):
            os.remove(full_path)
            
        db.session.delete(document)
        db.session.commit()
        flash('Document deleted', 'success')
    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'danger')
        
    return redirect(url_for('applications.view', id=document.application_id))

@applications_bp.route('/document/<int:doc_id>/download')
@login_required
def download_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    if document.application.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    directory = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id))
    return send_from_directory(directory, document.filename, as_attachment=True)

# --- Task Routes ---
@applications_bp.route('/<int:id>/add_task', methods=['POST'])
@login_required
def add_task(id):
    application = Application.query.get_or_404(id)
    if application.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
        
    description = request.form.get('description')
    if description:
        task = Task(description=description, application_id=application.id)
        db.session.add(task)
        db.session.commit()
        flash('Task added', 'success')
    
    return redirect(url_for('applications.view', id=id))

@applications_bp.route('/task/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.application.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
        
    task.is_completed = not task.is_completed
    db.session.commit()
    
    return jsonify({'success': True, 'is_completed': task.is_completed})

@applications_bp.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.application.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
        
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'success': True})
from datetime import timedelta  # Added for create function