from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User
from flask_login import current_user
from flaskblog.choices import CHOICES_TYPE_ISSUED, CHOICES_PERSON, CHOICES_LOCATION, CHOICES_MATERIALID, CHOICES_UNIT

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already exists')


class PostForm(FlaskForm):
    material_id = SelectField('Material ID', validators=[DataRequired()], choices=[(x, x) for x in CHOICES_MATERIALID])
    numbers_issued = IntegerField('Numbers', default=1, validators=[DataRequired()])
    unit = SelectField('Unit', default='pcs', choices=[(x, x) for x in CHOICES_UNIT])
    person = SelectField('Person', choices=CHOICES_PERSON, validators=[DataRequired()])
    location = SelectField('Location/Machine', default='Delhi', choices=CHOICES_LOCATION)
    type_issued = SelectField('Type Issued', default='CONSUMED', choices=CHOICES_TYPE_ISSUED)
    submit = SubmitField('Post')

class SortDays(FlaskForm):
    # for some reason the value of tuples below has to be strings and not ints
    sort_days = SelectField('Last Days', choices=[('All', 'All'), ('1', '1'),
                                                  ('7', '7'), ('30', '30'),
                                                  ('90', '90'), ('360', '360')])
    submit = SubmitField('Search')
    
