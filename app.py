from flask import Flask, render_template, redirect, flash, session, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Species, City, Country, SpeciesError
from forms import SignupForm, LoginForm
from typing import TypeVar

app = Flask(__name__)

app.config["SECRET_KEY"] = "kubrick"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///threatened-species"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SQLALCHEMY_ECHO"] = True

UserOrNone = TypeVar("UserOrNone", User, None)

debug = DebugToolbarExtension(app)
connect_db(app)

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

    # if city and/or country are not in db, add them 1st
    country_name = country
    city_name = city
    country_id = None
    city_id = None

    country = Country.query.filter_by(name=country_name).one_or_none()
    # if the country is in db, get its id
    if country:
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

    # otherwise, add the country and city to db
    else:
        # add country
        country = Country(name=country_name)
        db.session.add(country)
        db.session.commit()
        country_id = country.id

        # add city
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
    if session.get("current_user_id", None):
        species_name = request.args["species"]
        # if user clicks search on blank input, remove species from page
        if not species_name:
            if session.get("species_id"):
                del session["species_id"]
            return redirect("/home")
        try:
            species = Species.get_species(species_name)
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
            "You are not authorized for that action. Please first login or \
    create an account."
    user_id = session.get("current_user_id", None)
    if user_id:
        try:
            Species.add_species(species_id, user_id)
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
            "You are not authorized for that action. Please first login or \
    create an account."
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