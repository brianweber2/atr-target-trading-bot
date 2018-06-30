from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
	"""Form for logging in user."""
	username = StringField(
		'Username',
		validators=[DataRequired()],
		render_kw={"placeholder": "Username"}
	)
	password = PasswordField(
		'Password',
		validators=[DataRequired()],
		render_kw={"placeholder": "Password"}
	)
