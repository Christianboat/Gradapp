# filename: app/models.py
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    application_type = db.Column(db.String(50), nullable=False)
    institution = db.Column(db.String(200), nullable=False)
    program_role = db.Column(db.String(200))
    country = db.Column(db.String(100))
    deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='Not Started')
    application_url = db.Column(db.String(500))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Indexes
    __table_args__ = (
        db.Index('ix_application_user_status', 'user_id', 'status'),
        db.Index('ix_application_user_deadline', 'user_id', 'deadline'),
        db.Index('ix_application_user_type', 'user_id', 'application_type'),
    )

    # Relationships
    tasks = db.relationship('Task', backref='application', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='application', lazy='dynamic', cascade='all, delete-orphan')
    
    def is_overdue(self):
        if self.deadline:
            return self.deadline < date.today()
        return False
    
    def days_remaining(self):
        if self.deadline:
            delta = self.deadline - date.today()
            return delta.days
        return None
    
    def __repr__(self):
        return f'<Application {self.title}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)

    def __repr__(self):
        return f'<Task {self.description}>'

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_type = db.Column(db.String(50)) # e.g., 'resume', 'cover_letter', 'transcript', 'other'
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)

    def __repr__(self):
        return f'<Document {self.filename}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))