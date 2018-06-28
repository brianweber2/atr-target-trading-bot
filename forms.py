from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import (DataRequired, Email, ValidationError, Length,
																EqualTo)

from models import User

def email_exists(form, field):
	user_exists = User.objects.raw({"_id": field.data})
	if list(user_exists):
		raise ValidationError("User with that email already exists.")


class RegistrationForm(FlaskForm):
	"""Form for registering a new user."""
	first_name = StringField('First Name', validators=[DataRequired()])
	last_name = StringField('Last Name', validators=[DataRequired()])
	email = StringField(
		'Email',
		validators=[
			DataRequired(),
			Email(),
			email_exists
		]
	)
	password = PasswordField(
		'Password',
		validators=[
			DataRequired(),
			Length(min=8),
			EqualTo('password2', message='Passwords must match')
		]
	)
	password2 = PasswordField(
		'Confirm Password',
		validators=[DataRequired()]
	)


class LoginForm(FlaskForm):
	"""Form for logging in user."""
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
