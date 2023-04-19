from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class RegisterForm(FlaskForm):
    """User Register Form"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=6)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    profile_image = StringField('Profile Image URL')

