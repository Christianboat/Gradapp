# filename: app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateField, URLField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, URL
from wtforms.widgets import TextArea
from config import Config

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                          validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', 
                       validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', 
                            validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password',
                             validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', 
                       validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                            validators=[DataRequired()])
    remember_me = SelectField('Remember Me', 
                             choices=[('0', 'No'), ('7', '7 days'), ('30', '30 days')],
                             default='0')
    submit = SubmitField('Sign In')

class ApplicationForm(FlaskForm):
    title = StringField('Application Title*', 
                       validators=[DataRequired(), Length(max=200)],
                       description='e.g., "Stanford CS PhD Fall 2024"')
    application_type = SelectField('Type*', 
                                  choices=[('', 'Select Type')] + [(t, t) for t in Config.APPLICATION_TYPES],
                                  validators=[DataRequired()])
    institution = StringField('Institution/Company*', 
                             validators=[DataRequired(), Length(max=200)])
    program_role = StringField('Program/Role', 
                              validators=[Optional(), Length(max=200)],
                              description='Program name or job title')
    country = SelectField('Country', 
                         choices=[('', 'Select Country')] + [(c, c) for c in Config.COUNTRIES],
                         validators=[Optional()])
    deadline = DateField('Deadline*', 
                        validators=[DataRequired()],
                        format='%Y-%m-%d',
                        description='Format: YYYY-MM-DD')
    status = SelectField('Status', 
                        choices=[(s, s) for s in Config.STATUS_CHOICES],
                        default='Not Started')
    application_url = URLField('Application URL', 
                              validators=[Optional(), URL()],
                              description='Link to application portal')
    notes = TextAreaField('Notes', 
                         validators=[Optional()],
                         widget=TextArea(),
                         description='Any additional notes or reminders')
    submit = SubmitField('Save Application')