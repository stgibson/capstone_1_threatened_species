from unittest import TestCase
from models import db, User, Species, City, Country
from app import app
from sqlalchemy.exc import IntegrityError

app.config["TESTING"] = True
app.config["DEBUG_TB_HOST"] = ["dont-show-debug-toolbar"]
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///threatened-species-test"

db.create_all()

class SpeciesModelTestCase(TestCase):
    """
        Tests for columns and methods in Species model
    """

    def setUp(self):
        """
            Sets up database for next tests
        """

        User.query.delete()
        Species.query.delete()
        City.query.delete()
        Country.query.delete()

        self.test_species1 = {
            "name": "species1",
            "threatened": "VU"
        }

        self.test_species2 = {
            "name": "species2",
            "threatened": "VU"
        }

        self.sample_species_name = "loxodonta africana"
        
        self.client = app.test_client()

    def test_species_model(self):
        """
            Tests can create species with valid input
        """

        name1 = self.test_species1["name"]
        threatened = self.test_species1["threatened"]
        species1 = Species(name=name1, threatened=threatened)
        db.session.add(species1)
        db.session.commit()
        species1 = Species.query.filter_by(name=name1).one()
        species1_id = species1.id

        self.assertIsNotNone(species1_id)
        self.assertEqual(species1.name, name1)
        self.assertEqual(species1.threatened, threatened)
        self.assertEqual(
            species1.__repr__(),
            f'<Species id={species1_id} name="{name1}" \
threatened={threatened}>'
        )

        # test can create another species with same threatened level
        name2 = self.test_species2["name"]
        species2 = Species(name=name2, threatened=threatened)
        db.session.add(species2)
        db.session.commit()
        species2 = Species.query.filter_by(name=name2).one()
        species2_id = species1.id

        self.assertIsNotNone(species2_id)
        self.assertEqual(species2.name, name2)
        self.assertEqual(species2.threatened, threatened)

        # test if can access countries species exists in
        countries_list = [
            { "name": "Country1" },
            { "name": "Country2" }
        ]
        num_of_countries = len(countries_list)
        countries = [Country(name=country["name"]) for country in \
            countries_list]
        for country in countries:
            species1.countries.append(country)
        db.session.commit()

        self.assertEqual(len(species1.countries), num_of_countries)
        for i in range(num_of_countries):
            self.assertEqual(
                species1.countries[i].name,
                countries_list[i]["name"]
            )

        # test if can get users that like the species (1st add city for user)
        city = City(name="City", country_id=species1.countries[0].id)
        db.session.add(city)
        db.session.commit()
        city_id = city.id

        users_list = [
            {
                "username": "user1",
                "email": "email1@gmail.com",
                "password": "password",
            },
            {
                "username": "user2",
                "email": "email2@gmail.com",
                "password": "password",
            }
        ]
        num_of_users = len(users_list)
        users = [User(
            username=user["username"],
            email=user["email"],
            password=user["password"],
            city_id=city_id
        ) for user in users_list]
        for user in users:
            species1.users.append(user)
            db.session.commit()

        self.assertEqual(len(species1.users), num_of_users)
        for i in range(num_of_users):
            self.assertEqual(
                species1.users[i].username,
                users_list[i]["username"]
            )
            self.assertEqual(
                species1.users[i].email,
                users_list[i]["email"]
            )
            self.assertEqual(
                species1.users[i].password,
                users_list[i]["password"]
            )

    def test_species_model_fail(self):
        """
            Tests fail to create species with invalid input
        """

        # first create a species to test uniqueness constraints
        name1 = self.test_species1["name"]
        threatened1 = self.test_species1["threatened"]
        species = Species(name=name1, threatened=threatened1)
        db.session.add(species)
        db.session.commit()

        # now test creating a new species with invalid inputs
        threatened2 = self.test_species2["threatened"]

        # test not including name
        species = Species(threatened=threatened2)
        db.session.add(species)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # test using existing name
        species = Species(name=name1, threatened=threatened2)
        db.session.add(species)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_get_species(self):
        """
            Tests can get data on species only if it exists
        """

        # test if I can get a species that exists but isn't in db
        name = self.sample_species_name
        species = Species.get_species(name)

        self.assertIsNotNone(species)
        self.assertEqual(species.name, name)

        # test if I can get the same species not that it's in db
        species = Species.get_species(name)

        self.assertIsNotNone(species)
        self.assertEqual(species.name, name)

        # test that I can't get a species that doesn't exist
        # with self.assertRaises(SpeciesError):
        #     species = Species.get_species(name)

    # def test_add_species(self):
    #     """
    #         Tests can add species to user only if not already on user's list
    #     """

    #     # first add a species and a user for testing
    #     name = self.test_species1["name"]
    #     threatened = self.test_species1["threatened"]
    #     species = Species(name=name, threatened=threatened)
    #     db.session.add(species)
    #     db.session.commit()
    #     species_id = species.id
        
    #     country = Country(name="Country")
    #     db.session.add(country)
    #     db.session.commit()
    #     country_id = country.id

    #     city = City(name="City", country_id=country_id)
    #     db.session.add(country)
    #     db.session.commit()
    #     city_id = city.id

    #     username = "user"
    #     email = "email"
    #     password = "password"
    #     user = User(
    #         username=username,
    #         email=email,
    #         password=password,
    #         city_id=city_id
    #     )
    #     db.session.add(user)
    #     db.session.commit()
    #     user_id = user.id

    #     # test if can add species to user list
    #     Species.add_species(species_id, user_id)
    #     self.assertEqual(len(user.species), 1)
    #     self.assertEqual(user.species[0].name, name)
    #     self.assertEqual(user.species[0].threatened, threatened)

    #     # test that will get error if try to add species already on user's list
    #     with self.assertRaises(SpeciesError):
    #         Species.add_species(species_id, user_id)

    # def test_delete_species(self):
    #     """
    #         Tests can delete species from user only if in user's list
    #     """

    #     # first add a species to a new user's list
    #     name = self.test_species1["name"]
    #     threatened = self.test_species1["threatened"]
    #     species = Species(name=name, threatened=threatened)
    #     db.session.add(species)
    #     db.session.commit()
    #     species_id = species.id
        
    #     country = Country(name="Country")
    #     db.session.add(country)
    #     db.session.commit()
    #     country_id = country.id

    #     city = City(name="City", country_id=country_id)
    #     db.session.add(country)
    #     db.session.commit()
    #     city_id = city.id

    #     username = "user"
    #     email = "email"
    #     password = "password"
    #     user = User(
    #         username=username,
    #         email=email,
    #         password=password,
    #         city_id=city_id
    #     )
    #     db.session.add(user)
    #     db.session.commit()
    #     user_id = user.id

    #     user.species.append(species)
    #     db.session.commit()

    #     # test can delete species
    #     Species.delete_species(species_id, user_id)
    #     self.assertEqual(len(user.species), 0)

    #     # test that will get error if try to delete species
    #     with self.assertRaises(SpeciesError):
    #         Species.delete_species(species_id, user_id)