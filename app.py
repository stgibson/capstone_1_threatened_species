from flask import Flask, render_template, redirect, flash, session, request
from flask_debugtoolbar import DebugToolbarExtension
# from flask_mail import Mail, Message
from models import db, connect_db, User, Species, City, Country
from models import SpeciesError, CountryError
from forms import SignupForm, LoginForm, EditForm
from typing import TypeVar
import sendgrid
import os
from sendgrid.helpers.mail import *

sg = sendgrid.SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
from_email = Email("seanthomasgibson@gmail.com")

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "kubrick")
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = \
    os.environ.get("DATABASE_URL", "postgresql:///threatened-species")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# PASSWORD = os.environ.get("PASSWORD")

# mail_settings = {
#     "MAIL_SERVER": "smtp.gmail.com",
#     "TESTING": False,
#     "MAIL_DEBUG": True,
#     "MAIL_SUPPRESS_SEND": False,
#     "MAIL_PORT": 465,
#     "MAIL_USE_TLS": False,
#     "MAIL_USE_SSL": True,
#     "MAIL_USERNAME": "seanthomasgibson@gmail.com",
#     "MAIL_PASSWORD": PASSWORD
# }
# mail_settings = {

# }
# app.config.update(mail_settings)

UserOrNone = TypeVar("UserOrNone", User, None)
MATCH_NUM = int(os.environ.get("MATCH_NUM", 10))

debug = DebugToolbarExtension(app)
connect_db(app)

mail = Mail(app)

def create_user(
    username: str,
    email: str,
    password: str,
    city: str,
    country: str
) -> UserOrNone:
    """
        Creates new user with given credentials. If successful, returns new
        user, otherwise returns None.
        :type username: str
        :type email: str
        :type password: str
        :type city: str
        :type country: str
        :rtype: User | None
    """

    country_code = country
    city_name = city
    country_id = None
    city_id = None

    # country must be in db cause selected by user
    country = Country.query.filter_by(code=country_code).one()
    country_id = country.id

    city = City.query.filter_by(name=city_name).one_or_none()
    # if the city is in db, get its id
    if city:
        city_id = city.id
    # otherwise, add city to db
    else:
        city = City(name=city_name, country_id=country_id)
        db.session.add(city)
        db.session.commit()
        city_id = city.id

    # add user to db
    return User.signup(username, email, password, city_id)


def login(user_id: int) -> None:
    """
        Stores user_id in session
        :type user_id: int
    """

    session["current_user_id"] = user_id

def edit_profile(user_id: int, username: str, email: str, city: str, country: str) -> None:
    """
        Edits profile of user with id user_id
        :type user_id: in
        :type username: str
        :type email: str
        :type city: str
        :type country: str
    """

    user = User.query.get(user_id)
    user.username = username
    user.email = email
    db.session.add(user)
    db.session.commit()

    country_code = country
    city_name = city
    country_id =  None
    city_id = None
    if user.city.country.code == country_code:
        country_id = user.city.country.id
    if user.city.name == city_name:
        city_id = user.city.id

    if country_id:
        country = Country.query.get(country_id)
        # if city has changed, check if in country
        if not city_id:
            city_id_list = [city.id for city in country.cities if \
                city.name == city_name]
            if city_id_list:
                # should only be 1 city with that name in the country
                city_id = city_id_list[0]
                user.city_id = city_id
                db.session.add(user)
                db.session.commit()
            # otherwise need to add city to db
            else:
                city = City(name=city_name, country_id=country_id)
                db.session.add(city)
                db.session.commit()
                city_id = city.id
                user.city_id = city_id
                db.session.add(user)
                db.session.commit()
    # if country has changed, get new country and city
    else:
        country = Country.query.filter_by(code=country_code).one()
        country_id = country.id
        # even if city hasn't changed, since in different country, need to add
        city = City(name=city_name, country_id=country_id)
        db.session.add(city)
        db.session.commit()
        city_id = city.id
        user.city_id = city_id
        db.session.add(user)
        db.session.commit()

def is_match(species_id: int, city_id: int) -> bool:
    """
        If MATCH_NUM users in city with id city_id like species with id
        species_id, returns True, otherwise returns False
        :type species_id: int
        :type city_id: int
        :rtype: bool
    """

    city = City.query.get(city_id)
    num_of_users = 0
    # count number of users in city that have species with id species.id
    for user in city.users:
        for species in user.species:
            if species.id == species_id:
                num_of_users += 1
    flash(num_of_users, "info")
    flash(MATCH_NUM, "info")
    result = num_of_users == MATCH_NUM
    flash(result, "info")
    return result

def make_notification(species_id: int, user_id: int) -> str:
    """
        Generate message that shares all users other than user with id user_id
        who have species with id species_id in their list, that are in the same
        city as user with id user_id
        :type species_id: int
        :type user_id: int
        :rtype: str
    """

    user = User.query.get(user_id)
    species = Species.query.get(species_id)
    city_id = user.city_id
    notification = \
        f"Congratulations! You and {MATCH_NUM - 1} other people in \
{user.city.name}, {user.city.country.name} have {species.name} in their \
lists!  Here is a list of the other users:"
    # add users other than user with id user_id in city with id city_id to list
    for user in species.users:
        if user.city_id == city_id and user.id != user_id:
            notification += f"\n{user.username} ({user.email})"
    return notification

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
            flash(is_a_match, "info")
            if is_a_match:
                flash("match", "info")
                # send email to each user in the same city who like the species
                for user in [user for user in species.users if \
                    user.city_id == curr_user.city_id]:
                    notification = make_notification(species_id, user.id)
                    flash(notification, "info")
                    subject = subject("Threatened Species Website")
                    to_email = To(user.email)
                    content = PlainTextContent(notification)
                    mail = Mail(
                        from_email=from_email,
                        subject=subject,
                        to_email=to_email,
                        plain_text_content=content)
                    mail_json = mail.get()
                    # flash(mail_json, "info")
                    response = sg.send(message=mail_json)
                    flash(response.status_code, "info")
                    print(response.body)
                    print(response.headers)
                    # with app.app_context():
                    #     msg = Message(
                    #         subject="Threatened Species Website",
                    #         sender=app.config.get("MAIL_USERNAME"),
                    #         recipients=[user.email],
                    #         body=notification
                    #     )
                    #     mail.send(msg)
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
