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
        and the id of the city the user lives in.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.Text, nullable=False, unique=True)

    email = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

# class Species(db.Models):
#     """
#         Schema for species. Has species' id, name and threatened level.
#     """

#     __tablename__ = "species"

#     id = db.Column