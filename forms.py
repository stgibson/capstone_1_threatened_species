from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, DataRequired

class SignupForm(FlaskForm):
    """
        Template for form for users to sign up
    """

    username = StringField("Username", validators=[InputRequired()])

    email = StringField("Email", validators=[Email()])

    password = PasswordField("Password", validators=[InputRequired()])

    city = StringField("City", validators=[InputRequired()])

    country = StringField("Country", validators=[InputRequired()])

    accept_terms = BooleanField(
        "By checking this box, you understand and agree that if your list of \
species on the website has a match with a sufficient number of other users, \
then other users may be notified of your username and email address, and they \
also then be aware of which city you live in.",
        validators=[DataRequired()]
    )

class LoginForm(FlaskForm):
    """
        Template for form for users to login
    """

    username = StringField("Username", validators=[InputRequired()])

    password = PasswordField("Password", validators=[InputRequired()])