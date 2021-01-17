from models import db, User
from app import app

db.drop_all()
db.create_all()

# add sample users
sample_users = [
    {
        "username": "stgibson",
        "email": "stgibson@ucsc.edu",
        "password": "password"
    },
    {
        "username": "seangibson",
        "email": "seangibson@comcast.net",
        "password": "password"
    },
    {
        "username": "seanthomasgibson",
        "email": "seanthomasgibson@gmail.com",
        "password": "password"
    }
]
users = [User(username=user["username"], email=user["email"], \
    password=user["password"]) for user in sample_users]
db.session.add_all(users)
db.session.commit()