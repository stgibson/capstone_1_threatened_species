from unittest import TestCase
from models import db, User, Species, City, Country
from app import app
from sqlalchemy.exc import IntegrityError

app.config["TESTING"] = True
app.config["DEBUG_TB_HOST"] = ["dont-show-debug-toolbar"]
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///threatened-species-test"

db.create_all()

class UserModelTestCase(TestCase):
    """
        Tests for columns and methods in User model
    """

    def setUp(self):
        """
            Sets up database for next tests
        """

        User.query.delete()
        Species.query.delete()
        City.query.delete()
        Country.query.delete()

        # create city and country for user to live in
        country = Country(name="Test Country")
        db.session.add(country)
        db.session.commit()

        city = City(name="Test City", country_id=country.id)
        db.session.add(city)
        db.session.commit()
        self.test_city = city

        self.test_user1 = {
            "username": "testuser1",
            "email": "test1@gmail.com",
            "password": "password"
        }

        self.test_user2 = {
            "username": "testuser2",
            "email": "test2@gmail.com",
            "password": "password"
        }
        
        self.client = app.test_client()

    def test_user_model(self):
        """
            Tests can create user with valid input
        """

        username = self.test_user1["username"]
        email = self.test_user1["email"]
        password = self.test_user1["password"]
        city_id = self.test_city.id
        user = User(
            username=username,
            email=email,
            password=password,
            city_id=city_id
        )
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(username=username).one()
        user_id = user.id

        self.assertIsNotNone(user_id)
        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)
        self.assertEqual(user.password, password)
        self.assertEqual(user.city, self.test_city)
        self.assertEqual(user.__repr__(),
            f"<User id={user_id} username={username} email={email} \
password={password} city_id={city_id}>")

    def test_user_model_fail(self):
        """
            Tests fail to create user with invalid input
        """

        # first create a user to test uniqueness constraints
        username1 = self.test_user1["username"]
        email1 = self.test_user1["email"]
        password1 = self.test_user1["password"]
        city_id = self.test_city.id
        user = User(
            username=username1,
            email=email1,
            password=password1,
            city_id=city_id
        )
        db.session.add(user)
        db.session.commit()

        # now test creating a new user with invalid inputs
        username2 = self.test_user2["username"]
        email2 = self.test_user2["email"]
        password2 = self.test_user2["password"]

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

    # def test_signup(self):
    #     """
    #         Tests signup only creates a new user with valid input
    #     """
        
    #     # test for valid input
    #     username1 = self.test_user1["username"]
    #     email1 = self.test_user1["email"]
    #     password1 = self.test_user1["password"]
    #     city_id = self.test_city.id
    #     user = User.signup(username1, email1, password1, city_id)
          
    #     self.assertIsNotNone(user.id)
    #     self.assertEqual(user.username, username1)
    #     self.assertEqual(user.email, email1)
    #     # validate password is encrypted
    #     self.assertNotEqual(user.password, password1)
    #     self.assertEqual(user.city, self.test_city)

    #     # test for invalid input
    #     username2 = self.test_user2["username"]
    #     email2 = self.test_user2["email"]
    #     password2 = self.test_user2["password"]

    #     # test attempt to create account with existing username
    #     user = User.signup(username1, email2, password2, city_id)
    #     self.assertIsNone(user)

    #     # test attempt to create account with existing email
    #     user = User.signup(username2, email1, password2, city_id)
    #     self.assertIsNone(user)

    # def test_authenticate(self):
    #     """
    #         Tests authenticate only returns user when valid credentials
    #         provided
    #     """

    #     # test providing valid credentials
    #     username = self.test_user1["username"]
    #     password = self.test_user1["password"]
    #     user = User.authenticate(username, password)

    #     self.assertIsNotNone(user.id)
    #     self.assertEqual(user.username, username)
    #     # validate password is encrypted
    #     self.assertNotEqual(user.password, password)

    #     # test providing invalid credentials
    #     user = User.authenticate("wrong", password)
    #     self.assertIsNone(user)

    #     user = User.authenticate(username, "wrong")
    #     self.assertIsNone(user)