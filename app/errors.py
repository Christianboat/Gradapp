# filename: app/errors.py
from flask import render_template, request
from app import db

def page_not_found(e):
    return render_template('errors/404.html'), 404

def internal_server_error(e):
    db.session.rollback()
    return render_template('errors/500.html'), 500