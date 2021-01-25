from unittest import TestCase
from models import db, User, Species, City, Country, TOKEN, BASE_URL
from app import app, create_user, is_match, make_notification
from sqlalchemy.exc import IntegrityError

app.config["TESTING"] = True
app.config["DEBUG_TB_HOST"] = ["dont-show-debug-toolbar"]
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///threatened-species-test"

db.create_all()

class HelpersTestCase(TestCase):
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
        self.cities = ["City1", "City2"]

        # add country to db
        country_name = "Country"
        country_code = "CO"
        country = Country(name=country_name, code=country_code)
        db.session.add(country)
        db.session.commit()
        self.country_id = country.id
        self.country_code = country_code

        self.client = app.test_client()

    def test_create_user(self) -> None:
        """
            Tests can create user with username, email, password, city, and
            country.
        """

        # test if can create user in city not in db
        user1 = self.users[0]
        username1 = user1["username"]
        email1 = user1["email"]
        password1 = user1["password"]
        city_name = self.cities[0]
        country_id = self.country_id
        country_code = self.country_code
        user = create_user(
            username1,
            email1,
            password1,
            city_name,
            country_code
        )

        city = City.query.filter_by(name=city_name).one_or_none()
        self.assertIsNotNone(city)
        self.assertEqual(city.name, city_name)
        self.assertEqual(city.country_id, country_id)
        city_id = city.id

        self.assertIsNotNone(user)
        self.assertEqual(user.username, username1)
        self.assertEqual(user.email, email1)
        # verify encryption
        self.assertNotEqual(user.password, password1)
        self.assertEqual(user.city_id, city_id)   

        # test if can create user in city in db
        user2 = self.users[1]
        username2 = user2["username"]
        email2 = user2["email"]
        password2 = user2["password"]
        user = create_user(
            username2,
            email2,
            password2,
            city_name,
            country_code
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.username, username2)
        self.assertEqual(user.email, email2)
        # verify encryption
        self.assertNotEqual(user.password, password2)
        self.assertEqual(user.city_id, city_id) 

        # test that can't create user with existing username
        user3 = self.users[2]
        username3 = user3["username"]
        email3 = user3["email"]
        password3 = user3["password"]
        user = create_user(
            username2,
            email3,
            password3,
            city_name,
            country_code
        )
        self.assertIsNone(user)

        # test that can't create user with existing email
        user = create_user(
            username3,
            email2,
            password3,
            city_name,
            country_code
        )
        self.assertIsNone(user)

    def test_is_match(self) -> None:
        """
            Tests is_match(species_id) returns true only if species with id
            species_id in 10 species lists for users in the same city, and
            returns false otherwise
        """

        species_name = self.species["name"]
        species_threatened = self.species["threatened"]
        species = Species(name=species_name, threatened=species_threatened)
        db.session.add(species)
        db.session.commit()
        species_id = species.id

        country_id = self.country_id

        city_name1 = self.cities[0]
        city1 = City(name=city_name1, country_id=country_id)
        db.session.add(city1)
        db.session.commit()
        city_id1 = city1.id

        city_name2 = self.cities[1]
        city2 = City(name=city_name2, country_id=country_id)
        db.session.add(city2)
        db.session.commit()
        city_id2 = city2.id

        # test returns false if less than 10 users in same city
        num_of_users = len(self.users)
        for i in range(num_of_users - 2):
            user_data = self.users[i]
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"],
                city_id=city_id1
            )
            db.session.add(user)
            db.session.commit()
            user.species.append(species)
            db.session.commit()

        self.assertFalse(is_match(species_id, city_id1))

        # test returns false if 10 users but not in same city
        user_data = self.users[num_of_users - 2]
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
            city_id=city_id2
        )
        db.session.add(user)
        db.session.commit()
        user.species.append(species)
        db.session.commit()
        
        self.assertFalse(is_match(species_id, city_id1))

        # test returns true if 10 users in same city
        user.city_id = city_id1
        db.session.add(user)
        db.session.commit()

        self.assertTrue(is_match(species_id, city_id1))

        # test returns false if more than 10 users in same city
        user_data = self.users[num_of_users - 1]
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
            city_id=city_id1
        )
        db.session.add(user)
        db.session.commit()
        user.species.append(species)
        db.session.commit()

        self.assertFalse(is_match(species_id, city_id1))

    def test_make_notification(self):
        """
            Tests get correct notification
        """

        species_name = self.species["name"]
        species_threatened = self.species["threatened"]
        species = Species(name=species_name, threatened=species_threatened)
        db.session.add(species)
        db.session.commit()
        species_id = species.id

        country_id = self.country_id

        city_name1 = self.cities[0]
        city1 = City(name=city_name1, country_id=country_id)
        db.session.add(city1)
        db.session.commit()
        city_id1 = city1.id

        city_name2 = self.cities[1]
        city2 = City(name=city_name2, country_id=country_id)
        db.session.add(city2)
        db.session.commit()
        city_id2 = city2.id

        # add (num_of_users - 1) users in city1 and 1 user in city2
        num_of_users = len(self.users)
        for i in range(num_of_users - 1):
            user_data = self.users[i]
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"],
                city_id=city_id1
            )
            db.session.add(user)
            db.session.commit()
            user.species.append(species)
            db.session.commit()
        user_data = self.users[num_of_users - 1]
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
            city_id=city_id2
        )
        db.session.add(user)
        db.session.commit()
        user.species.append(species)
        db.session.commit()

        # make 2nd to last user get notification
        user = User.query.filter_by(
            username=self.users[num_of_users - 2]["username"]
        ).one()
        notification = make_notification(species_id, user.id)

        # test that all but last 2 users in notification
        for i in range(num_of_users - 2):
            username = self.users[i]["username"]
            email = self.users[i]["email"]
            self.assertIn(username, notification)
            self.assertIn(email, notification)
        for i in range(num_of_users - 2, num_of_users):
            username = self.users[i]["username"]
            email = self.users[i]["email"]
            self.assertNotIn(username, notification)
            self.assertNotIn(email, notification)