from unittest import TestCase
from models import db, User, Species, City, Country, TOKEN, BASE_URL
from app import app, create_user
from sqlalchemy.exc import IntegrityError

app.config["TESTING"] = True
app.config["DEBUG_TB_HOST"] = ["dont-show-debug-toolbar"]
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///threatened-species-test"
app.config["WTF_CSRF_ENABLED"] = False

db.create_all()

class HelpersTestCase(TestCase):
    """
        Tests helper functions in app.py
    """

    def setUp(self):
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
        self.countries = ["Country"]
        self.cities = ["City1", "City2"]

        self.client = app.test_client()

    def test_create_user(self):
        """
            Tests can create user with username, email, password, city, and
            country.
        """

        # test if can create user in country not in db
        user1 = self.users[0]
        country1 = self.countries[0]
        city1 = self.cities[0]
        user = create_user(
            user1["username"],
            user1["email"],
            user1["password"],
            city1,
            country1
        )

        country = Country.query.filter_by(name=country1).one_or_none()
        self.assertIsNotNone(country)
        self.assertEqual(country.name, country1)
        country_id = country.id

        city = City.query.filter_by(name=city1).one_or_none()
        self.assertIsNotNone(city)
        self.assertEqual(city.name, city1)
        self.assertEqual(city.country_id, country_id)
        city_id = city.id
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, user1["username"])
        self.assertEqual(user.email, user1["email"])
        # verify encryption
        self.assertNotEqual(user.password, user1["password"])
        self.assertEqual(user.city_id, city_id)

        # test if can create user in city not in db but in country in db
        user2 = self.users[1]
        city2 = self.cities[1]
        user = create_user(
            user2["username"],
            user2["email"],
            user2["password"],
            city2,
            country1
        )

        city = City.query.filter_by(name=city2).one_or_none()
        self.assertIsNotNone(city)
        self.assertEqual(city.name, city2)
        self.assertEqual(city.country_id, country_id)
        city_id = city.id

        self.assertIsNotNone(user)
        self.assertEqual(user.username, user2["username"])
        self.assertEqual(user.email, user2["email"])
        # verify encryption
        self.assertNotEqual(user.password, user2["password"])
        self.assertEqual(user.city_id, city_id)   

        # test if can create user in city and country in db
        user3 = self.users[2]
        user = create_user(
            user3["username"],
            user3["email"],
            user3["password"],
            city2,
            country1
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.username, user3["username"])
        self.assertEqual(user.email, user3["email"])
        # verify encryption
        self.assertNotEqual(user.password, user3["password"])
        self.assertEqual(user.city_id, city_id) 

        # test that can't create user with existing username
        user4 = self.users[3]
        user = create_user(
            user3["username"],
            user4["email"],
            user4["password"],
            city2,
            country1
        )
        self.assertIsNone(user)

        # test that can't create user with existing email
        user = create_user(
            user4["username"],
            user3["email"],
            user4["password"],
            city2,
            country1
        )
        self.assertIsNone(user)