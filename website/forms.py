from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

class LoginForm(FlaskForm):
    email = EmailField('Email adress', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email Address"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})


class RegisterForm(FlaskForm):
    email = EmailField('Email adress', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email Address"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message="Password must be greater than 8 characters"), Regexp( r'^(?=.*\d)(?=.*[\W_]).+$',  message="Password must contain at least one number and one special character") ,EqualTo('password2', message='Passwords must match')], render_kw={"placeholder": "Password"})
    password2 = PasswordField('Password (Confirm)', validators=[DataRequired()], render_kw={"placeholder": "Password (Confirm)"})
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30, message="Username must be greater than 3 characters"), Regexp(r'^[a-zA-Z0-9]+$', message="Username must be alphanumeric.")], render_kw={"placeholder": "Username"})
    firstname = StringField('First name', validators=[DataRequired(), Length(min=2, max=100, message="First name must be greater than 2 characters")], render_kw={"placeholder": "First Name"})
    lastname = StringField('Last name', validators=[DataRequired(), Length(min=2, max=100, message="Last name must be greater than 2 characters")], render_kw={"placeholder": "Last Name"})


class CSRFForm(FlaskForm):
    pass