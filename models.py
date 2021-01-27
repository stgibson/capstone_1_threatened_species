from __future__ import annotations
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
import requests

TOKEN = os.environ.get("TOKEN")
BASE_URL = "https://apiv3.iucnredlist.org/api/v3/"

db = SQLAlchemy()

bcrypt = Bcrypt()

class SpeciesError(Exception):
    """
        Exception for errors with using Species models
    """

    def __init__(self, message: str) -> None:
        """
            Constructor for SpeciesError
            :type message: str
        """

        self.message = message
        super().__init__(self.message)

class CountryError(Exception):
    """
        Exception for errors with using Country models
    """

    def __init__(self, message: str) -> None:
        """
            Constructor for CountryError
            :type message: str
        """

        self.message = message
        super().__init__(self.message)

def connect_db(app) -> None:
    """
        Connects app to db
        :type app: Flask
    """

    db.app = app
    db.init_app(app)

class User(db.Model):
    """
        Schema for users. Has user's id, username, email, a hashed password,
        and id of the city the user lives in.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.Text, nullable=False, unique=True)

    email = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    city_id = db.Column(
        db.ForeignKey("cities.id"),
        nullable=False
    )

    species = db.relationship(
        "Species",
        secondary="users_species",
        backref="users"
    )

    def __repr__(self) -> str:
        """
            Gets string representation of the user
            :rtype: str
        """

        return f"<User id={self.id} username={self.username} \
email={self.email} password={self.password} city_id={self.city_id}>"

    @classmethod
    def signup(cls, username: str, email: str, password: str, \
        city_id: int) -> User | None:
        """
            Creates a new user with given credentials. Returns new user unless
            an error occurs, in which case return None.
            :type username: str
            :type email: str
            :type password: str
            :type city_id: int
            :rtype: User
        """

        # first encrypt password
        hashed_password = \
            bcrypt.generate_password_hash(password).decode("utf8")

        user = cls(
            username=username,
            email=email,
            password=hashed_password,
            city_id=city_id
        )
        db.session.add(user)
        try:
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            return None

    @classmethod
    def authenticate(cls, username: str, password: str) -> User | None:
        """
            Determines if credentials are valid. If so, returns the appropriate
            user, otherwise returns None.
            :type username: str
            :type password: str
            :rtype: User
        """

        user = cls.query.filter_by(username=username).one_or_none()
        if (user):
            hashed_password = user.password

            if (bcrypt.check_password_hash(hashed_password, password)):
                return user
        return None

class Species(db.Model):
    """
        Schema for species. Has species' id, name and threatened level.
    """

    __tablename__ = "species"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text, nullable=False, unique=True)

    threatened = db.Column(db.Text, nullable=False)

    countries = db.relationship(
        "Country",
        secondary="species_countries",
        backref="species"
    )

    def __repr__(self) -> str:
        """
            Gets string representation of the species
            :rtype: str
        """

        # use quotes for species name since two words
        return f'<Species id={self.id} name="{self.name}" \
threatened={self.threatened}>'

    @classmethod
    def get_species(cls, species_name: str, country_id: int) -> Species | None:
        """
            Gets data of species with name species_name if it exists in country
            with id country_id, returns None otherwise
            :type species_name: str
            :type country_id: int
            :rtype: Species | None
        """

        # keep all letters lowercase for consistency in db
        species_name = species_name.lower()
        species = cls.query.filter_by(name=species_name).one_or_none()
        # if in db and species is in the country the user is in
        if species:
            if [country for country in species.countries if \
                country.id == country_id]:
                return species
            # if species exists but not in country, raise exception
            error_message = "that species is not in your country"
            raise SpeciesError(error_message)
        # otherwise, pull from external API
        name_supported_format = "%20".join(species_name.split(" "))
        params = { "token": TOKEN }
        try:
            resp = requests.get(
                f"{BASE_URL}species/{name_supported_format}",
                params=params
            )
            data = resp.json()
            name = data["name"]

            result = data["result"]
            threatened = result[0]["category"]
            species = cls(name=name, threatened=threatened)
            db.session.add(species)
            db.session.commit()

            # add countries species is in
            resp = requests.get(
                f"{BASE_URL}species/countries/name/{name_supported_format}",
                params=params
            )
            data = resp.json()
            result = data["result"]
            for country in result:
                code = country["code"]
                country = Country.query.filter_by(code=code).one()
                species.countries.append(country)
            db.session.commit()

        except:
            db.session.rollback()
            error_message = "Could not find species"
            raise SpeciesError(error_message)
        if [country for country in species.countries if \
            country.id == country_id]:
            return species
        # if species exists but not in country, raise exception
        error_message = "that species is not in your country"
        raise SpeciesError(error_message)

    @classmethod
    def add_species(cls, species_id: int, user_id: int) -> None:
        """
            Adds species with id species_id to list of species of user with id
            user_id. If species_id already on user's list, raise exception.
            :type species_id: int
            :type user_id: int
            :rtype: None
        """
        
        user = User.query.get(user_id)
        # if user has already added species to list, raise exception
        if [species for species in user.species if species.id == species_id]:
            species = cls.query.get(species_id)
            error_message = \
                f"You have already added species {species.name} to your list"
            raise SpeciesError(error_message)
        else:
            # might fail if user uses a request app to submit request
            try: 
                species = cls.query.get(species_id)
                user.species.append(species)
                db.session.commit()
            except:
                db.session.rollback()
                raise SpeciesError("Invalid address")

    @classmethod
    def delete_species(cls, species_id: int, user_id: int) -> None:
        """
            Deletes species with id species_id from list of species of user
            with id user_id, or raises an exception if species isn't on the
            list
            :type species_id: int
            :type user_id: int
            :rtype: None
        """

        user = User.query.get(user_id)
        try:
            species = cls.query.get(species_id)
            user.species.remove(species)
            db.session.commit()
        except:
            db.session.rollback()
            error_message = "You do not have that species in your list"
            raise SpeciesError(error_message)

class City(db.Model):
    """
        Schema for cities. Has city's id, name, and id of the country it's in.
    """

    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text, nullable=False)

    country_id = db.Column(
        db.Integer,
        db.ForeignKey("countries.id"),
        nullable=False
    )

    users = db.relationship("User", backref="city")

    def __repr__(self) -> str:
        """
            Gets string representation of the city
            :rtype: str
        """

        return f"<City id={self.id} name={self.name} \
country_id={self.country_id}>"

class Country(db.Model):
    """
        Schema for countries. Has country's id and name.
    """

    __tablename__ = "countries"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text, nullable=False, unique=True)

    code = db.Column(db.Text, nullable=False, unique=True)

    cities = db.relationship("City", backref="country")

    def __repr__(self) -> str:
        """
            Gets string representation of the country
            :rtype: str
        """

        return f"<Country id={self.id} name={self.name} code={self.code}>"

    @classmethod
    def get_countries(cls):
        """
            Gets all countries from Red List API
        """

        params = { "token": TOKEN }
        try:
            resp = requests.get(f"{BASE_URL}country/list", params=params)
            data = resp.json()
            results = data["results"]
            for result in results:
                country = Country(
                    name=result["country"],
                    code=result["isocode"]
                )
                db.session.add(country)
            db.session.commit()
        except:
            db.session.rollback()
            error_message = "Could not load countries"
            raise CountryError(error_message)

class User_Species(db.Model):
    """
        Schema to connect users to species
    """

    __tablename__ = "users_species"

    user_id = db.Column(
        db.ForeignKey("users.id", ondelete="cascade"),
        primary_key=True
    )

    species_id = db.Column(
        db.ForeignKey("species.id", ondelete="cascade"),
        primary_key=True
    )

    def __repr__(self) -> str:
        """
            Gets string representation of the relationship between a user and a
            species
            :rtype: str
        """

        return f"<User_Species id={self.id} user_id={self.user_id} \
species_id={self.species_id}>"

class Species_Country(db.Model):
    """
        Schema to connect species to countries
    """

    __tablename__ = "species_countries"

    species_id = db.Column(
        db.ForeignKey("species.id", ondelete="cascade"),
        primary_key=True
    )

    country_id = db.Column(
        db.ForeignKey("countries.id", ondelete="cascade"),
        primary_key=True
    )

    def __repr__(self) -> str:
        """
            Gets string representation of the relationship between a species
            and a country
            :rtype: str
        """

        return f"<Species_Country id={self.id} species_id={self.species_id} \
country_id={self.country_id}>"