from __future__ import annotations
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
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
        db.ForeignKey("cities.id", ondelete="cascade"),
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

    threatened = db.Column(db.Text)

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

class City(db.Model):
    """
        Schema for cities. Has city's id, name, and id of the country it's in.
    """

    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text, nullable=False)

    country_id = db.Column(
        db.Integer,
        db.ForeignKey("countries.id", ondelete="cascade"),
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

    cities = db.relationship("City", backref="country")

    def __repr__(self) -> str:
        """
            Gets string representation of the country
            :rtype: str
        """

        return f"<Country id={self.id} name={self.name}>"

class User_Species(db.Model):
    """
        Schema to connect users to species
    """

    __tablename__ = "users_species"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

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