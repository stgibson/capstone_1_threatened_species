from unittest import TestCase
from models import db, User, Species, City, Country, SpeciesError
from app import app
from sqlalchemy.exc import IntegrityError

app.config["TESTING"] = True
app.config["DEBUG_TB_HOST"] = ["dont-show-debug-toolbar"]
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///threatened-species-test"

db.drop_all()
db.create_all()

class CountryModelTestCase(TestCase):
    """
        Tests for columns and methods in Country model
    """

    def setUp(self) -> None:
        """
            Sets up database for next tests
        """

        User.query.delete()
        Species.query.delete()
        City.query.delete()
        Country.query.delete()

        self.country1 = { "name": "Country 1", "code": "C1" }
        self.country2 = { "name": "Country 2", "code": "C2" }
        
        self.client = app.test_client()

    def test_country_model(self) -> None:
        """
            Tests can create country with valid input
        """

        name = self.country1["name"]
        code = self.country1["code"]
        country = Country(name=name, code=code)
        db.session.add(country)
        db.session.commit()
        country = Country.query.filter_by(name=name).one()
        country_id = country.id

        self.assertIsNotNone(country_id)
        self.assertEqual(country.name, name)
        self.assertEqual(country.code, code)
        self.assertEqual(
            country.__repr__(),
            f"<Country id={country_id} name={country.name} \
code={country.code}>"
        )

        # test can add and access species in country
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
            country.species.append(species)
            db.session.commit()

        self.assertEqual(len(country.species), num_of_species)
        for i in range(num_of_species):
            self.assertEqual(country.species[i].name, species_list[i]["name"])
            self.assertEqual(
                country.species[i].threatened,
                species_list[i]["threatened"]
            )

    def test_country_model_fail(self) -> None:
        """
            Tests fail to create country with invalid input
        """

        # first create a country to test uniqueness constraints
        name1 = self.country1["name"]
        code1 = self.country1["code"]
        country = Country(name=name1, code=code1)
        db.session.add(country)
        db.session.commit()

        name2 = self.country2["name"]
        code2 = self.country2["code"]

        # test not including name
        country = Country(code=code2)
        db.session.add(country)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # test not including code
        country = Country(name=name2)
        db.session.add(country)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # test using existing name
        country = Country(name=name1, code=code2)
        db.session.add(country)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # test using existing code
        country = Country(name=name2, code=code1)
        db.session.add(country)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    # def test_get_countries(self) -> None:
    #     """
    #         Tests can get countries from external API
    #     """

