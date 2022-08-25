from logging.config import valid_ident
from wsgiref.validate import validator
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError    
from tukevoting.models import Voter, Admin, Candidate

class RegistrationForm(FlaskForm):
    voter_id = StringField('Voter ID', validators=[DataRequired(), Length(min=2, max=20)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=15)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = Voter.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('email is already linked to another account')

    def validate_voter_id(self, voter_id):
        user = Voter.query.filter_by(voter_id=voter_id.data).first()
        if user:
            raise ValidationError('Voter ID is already linked to another account')



class LoginForm(FlaskForm):
    voter_id = StringField('Voter ID', validators=[DataRequired(), Length(min=5, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class AdminForm(FlaskForm):
    admin_id = StringField('Admin ID', validators=[DataRequired(), Length(min=2, max=20)])   
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class CandidateForm(FlaskForm):
    candidate_id = StringField('Candidate ID', validators=[DataRequired(), Length(min=12, max=20)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=4, max=15)])
    last_name = StringField('Second Name', validators=[DataRequired(), Length(min=4, max=15)])
    description = TextAreaField('Manifesto', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired(), Length(min=4, max=15)])
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'png'])])
    school = StringField('School', validators=[DataRequired(), Length(min=3, max=6)])
    submit = SubmitField('Submit Info')


class UpdateAccountForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=15)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Voter.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('email is already linked to another account')

    def validate_first_name(self, first_name):
        if first_name.data != current_user.first_name:
            user = Voter.query.filter_by(voter_id=first_name.data).first()
            if user:
                raise ValidationError('Voter ID is already linked to another account')
    
    def validate_last_name(self, last_name):
        if last_name.data != current_user.last_name:
            user = Voter.query.filter_by(voter_id=last_name.data).first()
            if user:
                raise ValidationError('Voter ID is already linked to another account')

class SchoolForm(FlaskForm):
    school = SelectField('School', choices=[('SCIT', 'School of Information Technology'), ('SEEE', 'School of Electrical and Electronic Engineering'), ('SCAM', 'School of Creative Arts and Media')])
    delegate = SelectField('Delegate', choices=[])
    school_rep = SelectField('School Representative', choices=[])
