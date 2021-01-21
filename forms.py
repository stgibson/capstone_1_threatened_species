from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email

class SignupForm(FlaskForm):
    """
        Template for form for users to sign up
    """

    username = StringField("Username", validators=[InputRequired()])

    email = StringField("Email", validators=[Email()])

    password = PasswordField("Password", validators=[InputRequired()])

    city = StringField("City", validators=[InputRequired()])

    country = StringField("Country", validators=[InputRequired()])

class LoginForm(FlaskForm):
    """
        Template for form for users to login
    """

    username = StringField("Username", validators=[InputRequired()])

    password = PasswordField("Password", validators=[InputRequired()])