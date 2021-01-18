from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

    name = db.Column(db.Text, nullable=False, unique=True)

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
        nullable=False
    )

    species_id = db.Column(
        db.ForeignKey("species.id", ondelete="cascade"),
        nullable=False
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
        nullable=False
    )

    country_id = db.Column(
        db.ForeignKey("countries.id", ondelete="cascade"),
        nullable=False
    )

    def __repr__(self) -> str:
        """
            Gets string representation of the relationship between a species
            and a country
            :rtype: str
        """

        return f"<Species_Country id={self.id} species_id={self.species_id} \
country_id={self.country_id}>"