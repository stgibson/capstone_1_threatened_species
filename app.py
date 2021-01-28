from flask import Flask, render_template, redirect, flash, session, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, Message
from models import db, connect_db, User, Species, City, Country
from models import SpeciesError, CountryError
from forms import SignupForm, LoginForm, EditForm
from helpers import *
from typing import TypeVar
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "kubrick")
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = \
    os.environ.get("DATABASE_URL", "postgresql:///threatened-species")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

PASSWORD = os.environ.get("PASSWORD")

mail_settings = {
    "MAIL_SERVER": "smtp.gmail.com",
    "TESTING": False,
    "MAIL_DEBUG": True,
    "MAIL_SUPPRESS_SEND": False,
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": "seanthomasgibson@gmail.com",
    "MAIL_PASSWORD": PASSWORD
}
app.config.update(mail_settings)

UserOrNone = TypeVar("UserOrNone", User, None)
MATCH_NUM = int(os.environ.get("MATCH_NUM", 10))

debug = DebugToolbarExtension(app)
connect_db(app)

mail = Mail(app)

@app.route("/")
def go_to_home_page() -> str:
    """
        Base url goes to home page if the user is logged in, otherwise goes to
        login page.
        :rtype: str
    """

    if session.get("current_user_id", None):
        return redirect("/home")
    return redirect("/login")

@app.route("/signup", methods=["GET", "POST"])
def signup_form() -> str:
    """
        If GET request, displays signup form. If POST request, tries to create
        a new account for user. If successfully creates an account, logs in
        user and redirects to home page, otherwise redirects back to signup
        page with error message.
        :rtype: str
    """

    # first verify that user isn't already logged in
    info_message = "You are already logged in!"
    if session.get("current_user_id", None):
        flash(info_message, "info")
        return redirect("/home")

    error_message = \
        "That username or email has already been taken. Please try again."
    form = SignupForm()

    # get countries for user to select
    countries = Country.query.all()
    # if first time a user goes on this page, need to pull from API
    if len(countries) == 0:
        try:
            Country.get_countries()
            countries = Country.query.all()
        except CountryError as exc:
            flash(exc.message, "danger")
            return redirect("/")
    country_choices = []
    for country in countries:
        country_choices.append((country.code, country.name))
    form.country.choices = country_choices

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        city = form.city.data
        country = form.country.data
        user = create_user(username, email, password, city, country)
        if user:
            login(user.id)
            return redirect("/home")
        flash(error_message, "danger")
        return redirect("/signup")
    return render_template("signup.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login_form() -> str:
    """
        If GET request, displays login form. If POST request, tries to login
        user. If login is successful, redirects to home page, otherwise
        redirects back to login page with error message.
        :rtype: str
    """

    # first verify that user isn't already logged in
    info_message = "You are already logged in!"
    if session.get("current_user_id", None):
        flash(info_message, "info")
        return redirect("/home")

    error_message = "Invalid credentials. Please try again."
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            login(user.id)
            return redirect("/home")
        flash(error_message, "danger")
        return redirect("/login")
    return render_template("login.html", form=form)

@app.route("/about")
def show_about_page() -> str:
    """
        Shows the about page
        :rtype: str
    """

    return render_template("about.html")

@app.route("/logout")
def logout() -> str:
    """
        Deletes user from session and redirects to login page
        :rtype: str
    """

    if session.get("current_user_id", None):
        del session["current_user_id"]
    else:
        flash("You are already logged out", "info")
    if session.get("species_id"):
        del session["species_id"]
    return redirect("/login")

@app.route("/home")
def show_home_page() -> str:
    """
        Shows home page, along with list of user's liked species and a search
        form to get data on species and add them to the user's list
        :rtype: str
    """

    error_message = \
        "You are not authorized to access that page. Please first login or \
create an account."
    user_id = session.get("current_user_id", None)
    if user_id:
        user = User.query.get(user_id)

        species_id = session.get("species_id", None)
        if species_id:
            species = Species.query.get(species_id)
            return render_template("home.html", user=user, species=species)

        return render_template("home.html", user=user)

    flash(error_message, "danger")
    return redirect("/login")

@app.route("/species")
def get_species_data() -> str:
    """
        Gets data on species user searched for, and adds it to the session if
        it exists, otherwise lets user know the species doesn't exist
        :rtype: str
    """

    error_message = \
        "You are not authorized to access that page. Please first login or \
create an account."
    user_id = session.get("current_user_id", None)
    if user_id:
        user = User.query.get(user_id)
        species_name = request.args["species"]
        # if user clicks search on blank input, remove species from page
        if not species_name:
            if session.get("species_id"):
                del session["species_id"]
            return redirect("/home")
        try:
            species = Species.get_species(species_name, user.city.country.id)
            session["species_id"] = species.id
        except SpeciesError as exc:
            if session.get("species_id", None):
                del session["species_id"]
            flash(exc.message, "danger")
        finally:
            return redirect("/home")
    flash(error_message, "danger")
    return redirect("/login")

@app.route("/species/<int:species_id>", methods=["POST"])
def add_species_to_list(species_id: int) -> str:
    """
        Adds species to user's list. If the species is already on user's list,
        let user know.
        :type species_id: int
        :rtype: str
    """

    error_message = \
        "You are not authorized for that action. Please first login or create \
an account."
    user_id = session.get("current_user_id", None)
    if user_id:
        try:
            Species.add_species(species_id, user_id)

            # after adding species, doesn't need to be on left side of page
            if session.get("species_id", None):
                del session["species_id"]

            # check if should notify user of other users who like the species
            curr_user = User.query.get(user_id)
            species = Species.query.get(species_id)
            is_a_match = is_match(species_id, curr_user.city_id)
            if is_a_match:
                # send email to each user in the same city who like the species
                for user in [user for user in species.users if \
                    user.city_id == curr_user.city_id]:
                    notification = make_notification(species_id, user.id)
                    with app.app_context():
                        msg = Message(
                            subject="Threatened Species Website",
                            sender=app.config.get("MAIL_USERNAME"),
                            recipients=[user.email],
                            body=notification
                        )
                        mail.send(msg)
            return redirect("/home")

        except SpeciesError as exc:
            flash(exc.message, "danger")
        finally:
            return redirect("/home")
    flash(error_message, "danger")
    return redirect("/login")

@app.route("/species/<int:species_id>/delete", methods=["POST"])
def delete_species_from_list(species_id: int) -> str:
    """
        Deletes species from user's list. If the species isn't on user's list,
        lets user know.
        :type species_id: int
        :rtype: str
    """

    error_message = \
        "You are not authorized for that action. Please first login or create \
an account."
    user_id = session.get("current_user_id", None)
    if user_id:
        try:
            Species.delete_species(species_id, user_id)
        except SpeciesError as exc:
            flash(exc.message, "danger")
        finally:
            return redirect("/home")
    flash(error_message, "danger")
    return redirect("/login")

@app.route("/edit", methods=["GET", "POST"])
def edit_profile_form() -> str:
    """
        Edits user's profile, provided they entered valid credentials
        :rtype: str
    """

    error_message = \
        "You are not authorized for that action. Please first login or \
create an account."
    user_id = session.get("current_user_id", None)
    if user_id:
        user = User.query.get(user_id)
        form = EditForm(username=user.username, email=user.email, city=user.city.name, country=user.city.country.code)

        # get countries for user to select
        countries = Country.query.all()
        # if first time a user goes on this page, need to pull from API
        if len(countries) == 0:
            try:
                Country.get_countries()
                countries = Country.query.all()
            except CountryError as exc:
                flash(exc.message, "danger")
                return redirect("/")
        country_choices = []
        for country in countries:
            country_choices.append((country.code, country.name))
        form.country.choices = country_choices

        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            city = form.city.data
            country = form.country.data
            password = form.password.data

            # if user typed in right password, make changes
            if User.authenticate(user.username, password):
                edit_profile(user_id, username, email, city, country)
                return redirect("/")
            # otherwise, flash error message
            flash("Incorrect password. Could not edit profile.", "danger")
            return redirect("/edit")
        return render_template("edit.html", form=form)

    flash(error_message, "danger")
    return redirect("/login")

@app.route("/delete", methods=["POST"])
def delete_user() -> str:
    """
        Deletes the user's account only if the user is logged in
        :rtype: str
    """

    error_message = \
        "You are not authorized for that action. Please first login or create \
create an account."
    user_id = session.get("current_user_id", None)
    password = request.form["password"]
    if user_id:
        user = User.query.get(user_id)
        if User.authenticate(user.username, password):
            db.session.delete(user)
            db.session.commit()
            del session["current_user_id"]
            flash("Your account has been deleted", "info")
            return redirect("/login")
        flash("Incorrect password. Could not delete account.", "danger")
        return redirect("/edit")

    flash(error_message, "danger")
    return redirect("/login")
