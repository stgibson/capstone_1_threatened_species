from unittest import TestCase
from models import db, User, Species, City, Country, TOKEN, BASE_URL
from app import app, create_user, is_match, make_notification
from sqlalchemy.exc import IntegrityError

app.config["TESTING"] = True
app.config["DEBUG_TB_HOST"] = ["dont-show-debug-toolbar"]
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///threatened-species-test"
app.config["WTF_CSRF_ENABLED"] = False

db.create_all()

class FlaskTestCase(TestCase):
    """
        Tests helper functions in app.py
    """

    def setUp(self) -> None:
        """
            Sets up database for next tests
        """

        User.query.delete()
        Species.query.delete()
        City.query.delete()
        Country.query.delete()

        self.users = [
            {
                "username": "user1",
                "email": "user1@gmail.com",
                "password": "password"
            },
            {
                "username": "user2",
                "email": "user2@gmail.com",
                "password": "password"
            },
            {
                "username": "user3",
                "email": "user3@gmail.com",
                "password": "password"
            },
            {
                "username": "user4",
                "email": "user4@gmail.com",
                "password": "password"
            },
            {
                "username": "user5",
                "email": "user5@gmail.com",
                "password": "password"
            },
            {
                "username": "user6",
                "email": "user6@gmail.com",
                "password": "password"
            },
            {
                "username": "user7",
                "email": "user7@gmail.com",
                "password": "password"
            },
            {
                "username": "user8",
                "email": "user8@gmail.com",
                "password": "password"
            },
            {
                "username": "user9",
                "email": "user9@gmail.com",
                "password": "password"
            },
            {
                "username": "user10",
                "email": "user10@gmail.com",
                "password": "password"
            },
            {
                "username": "user11",
                "email": "user11@gmail.com",
                "password": "password"
            }
        ]
        self.species = { "name": "species", "threatened": "VU" }
        self.city = "City1"

        # add country to db
        country_name = "Country"
        country_code = "CO"
        country = Country(name=country_name, code=country_code)
        db.session.add(country)
        db.session.commit()
        self.country_id = country.id

        self.client = app.test_client()

    def test_add_species_to_list(self) -> None:
        """
            Test can add species to list only if not already on list, and get
            notification of other users only when expected
        """

        # setup species, country, and cities
        species_name = self.species["name"]
        species_threatened = self.species["threatened"]
        species = Species(name=species_name, threatened=species_threatened)
        db.session.add(species)
        db.session.commit()
        species_id = species.id

        city_name = self.city
        city = City(name=city_name, country_id=self.country_id)
        db.session.add(city)
        db.session.commit()
        city_id = city.id

        # create accounts for users
        num_of_users = len(self.users)
        for i in range(num_of_users - 1):
            username = self.users[i]["username"]
            email = self.users[i]["email"]
            password = self.users[i]["password"]
            user = User(
                username=username,
                email=email,
                password=password,
                city_id=city_id
            )
            db.session.add(user)
            db.session.commit()
        username = self.users[num_of_users - 1]["username"]
        email = self.users[num_of_users - 1]["email"]
        password = self.users[num_of_users - 1]["password"]
        user = User(
            username=username,
            email=email,
            password=password,
            city_id=city_id
        )
        db.session.add(user)
        db.session.commit()

        # add species to list
        with self.client as c:
            for i in range(num_of_users):
                username = self.users[i]["username"]
                user = User.query.filter_by(username=username).one()

                # log user in
                with c.session_transaction() as change_session:
                    change_session["current_user_id"] = user.id

                resp = c.post(f"/species/{species_id}", follow_redirects=True)
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn(species_name, html)
                self.assertIn(species_threatened, html)
                self.assertIn(f"/species/{species_id}/delete", html)
                # only (num_of_user - 2) user should get message
                if i == num_of_users - 2:
                    self.assertIn("Congratulations", html)
                    for i in range(num_of_users - 2):
                        self.assertIn(self.users[i]["username"], html)
                        self.assertIn(self.users[i]["email"], html)
                else:
                    self.assertNotIn("Congratulations", html)