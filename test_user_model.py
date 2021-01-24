from unittest import TestCase
from models import db, User, Species, City, Country
from app import app
from sqlalchemy.exc import IntegrityError

app.config["TESTING"] = True
app.config["DEBUG_TB_HOST"] = ["dont-show-debug-toolbar"]
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///threatened-species-test"

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """
        Tests for columns and methods in User model
    """

    def setUp(self) -> None:
        """
            Sets up database for next tests
        """

        User.query.delete()
        Species.query.delete()
        City.query.delete()
        Country.query.delete()

        # create city and country for user to live in
        country = Country(name="Country", code="CO")
        db.session.add(country)
        db.session.commit()

        city = City(name="City", country_id=country.id)
        db.session.add(city)
        db.session.commit()
        self.city = city

        self.user1 = {
            "username": "user1",
            "email": "email1@gmail.com",
            "password": "password"
        }

        self.user2 = {
            "username": "user2",
            "email": "email2@gmail.com",
            "password": "password"
        }
        
        self.client = app.test_client()

    def test_user_model(self) -> None:
        """
            Tests can create user with valid input
        """

        username1 = self.user1["username"]
        email1 = self.user1["email"]
        password = self.user1["password"]
        city_id = self.city.id
        user1 = User(
            username=username1,
            email=email1,
            password=password,
            city_id=city_id
        )
        db.session.add(user1)
        db.session.commit()
        user1 = User.query.filter_by(username=username1).one()
        user1_id = user1.id

        self.assertIsNotNone(user1_id)
        self.assertEqual(user1.username, username1)
        self.assertEqual(user1.email, email1)
        self.assertEqual(user1.password, password)
        self.assertEqual(user1.city, self.city)
        self.assertEqual(
            user1.__repr__(),
            f"<User id={user1_id} username={username1} email={email1} \
password={password} city_id={city_id}>"
        )

        # test can add users with same password and same city id
        username2 = self.user2["username"]
        email2 = self.user2["email"]
        user2 = User(
            username=username2,
            email=email2,
            password=password,
            city_id=city_id
        )
        db.session.add(user2)
        db.session.commit()
        user2 = User.query.filter_by(username=username2).one()
        user2_id = user2.id

        self.assertIsNotNone(user2_id)
        self.assertEqual(user2.username, username2)
        self.assertEqual(user2.email, email2)
        self.assertEqual(user2.password, password)
        self.assertEqual(user2.city, self.city)

        # also test if can get species user likes
        species_list = [
            { "name": "species1", "threatened": "VU" },
            { "name": "species2", "threatened": "VU" },
            { "name": "species3", "threatened": "VU" }
        ]
        num_of_species = len(species_list)
        all_species = [Species(
            name=species["name"],
            threatened=species["threatened"]
        ) for species in species_list]
        for species in all_species:
            user1.species.append(species)
            db.session.commit()

        self.assertEqual(len(user1.species), num_of_species)
        for i in range(num_of_species):
            self.assertEqual(user1.species[i].name, species_list[i]["name"])
            self.assertEqual(
                user1.species[i].threatened,
                species_list[i]["threatened"]
            )

    def test_user_model_fail(self) -> None:
        """
            Tests fail to create user with invalid input
        """

        # first create a user to test uniqueness constraints
        username1 = self.user1["username"]
        email1 = self.user1["email"]
        password1 = self.user1["password"]
        city_id = self.city.id
        user = User(
            username=username1,
            email=email1,
            password=password1,
            city_id=city_id
        )
        db.session.add(user)
        db.session.commit()

        # now test creating a new user with invalid inputs
        username2 = self.user2["username"]
        email2 = self.user2["email"]
        password2 = self.user2["password"]

        # test not including username
        user = User(email=email2, password=password2, city_id=city_id)
        db.session.add(user)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # test not including email
        user = User(username=username2, password=password2, city_id=city_id)
        db.session.add(user)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # test not including password
        user = User(username=username2, email=email2, city_id=city_id)
        db.session.add(user)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # test not including city id
        user = User(username=username2, email=email2, password=password2)
        db.session.add(user)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # test using existing username
        user = User(
            username=username1,
            email=email2,
            password=password2,
            city_id=city_id
        )
        db.session.add(user)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # test using existing password
        user = User(
            username=username2,
            email=email1,
            password=password2,
            city_id=city_id
        )
        db.session.add(user)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_signup(self) -> None:
        """
            Tests signup only creates a new user with valid input
        """
        
        # test for valid input
        username1 = self.user1["username"]
        email1 = self.user1["email"]
        password1 = self.user1["password"]
        city_id = self.city.id
        user = User.signup(username1, email1, password1, city_id)
          
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, username1)
        self.assertEqual(user.email, email1)
        # validate password is encrypted
        self.assertNotEqual(user.password, password1)
        self.assertEqual(user.city, self.city)

        # test for invalid input
        username2 = self.user2["username"]
        email2 = self.user2["email"]
        password2 = self.user2["password"]

        # test attempt to create account with existing username
        user = User.signup(username1, email2, password2, city_id)
        self.assertIsNone(user)

        # test attempt to create account with existing email
        user = User.signup(username2, email1, password2, city_id)
        self.assertIsNone(user)

    def test_authenticate(self) -> None:
        """
            Tests authenticate only returns user when valid credentials
            provided
        """

        # first create an account
        username = self.user1["username"]
        email = self.user1["email"]
        password = self.user1["password"]
        city_id = self.city.id
        User.signup(username, email, password, city_id)

        # test providing valid credentials
        user = User.authenticate(username, password)

        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, username)
        # validate password is encrypted
        self.assertNotEqual(user.password, password)

        # test providing invalid credentials
        user = User.authenticate("wrong", password)
        self.assertIsNone(user)

        user = User.authenticate(username, "wrong")
        self.assertIsNone(user)