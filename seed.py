from models import db, User, Species, City, Country, User_Species, \
    Species_Country
from app import app

db.drop_all()
db.create_all()

# add sample countries
sample_countries = [
    {
        "name": "United States"
    },
    {
        "name": "Canada"
    },
    {
        "name": "United Kingdom"
    }
]
countries = [Country(name=country["name"]) for country in sample_countries]
db.session.add_all(countries)
db.session.commit()

# add sample cities
sample_cities = [
    {
        "name": "San Ramon",
        "country_id": countries[0].id
    },
    {
        "name": "New York City",
        "country_id": countries[0].id
    },
    {
        "name": "Vancouver",
        "country_id": countries[1].id
    },
    {
        "name": "London",
        "country_id": countries[2].id
    }
]
cities = [City(name=city["name"], country_id=city["country_id"]) for city in \
    sample_cities]
db.session.add_all(cities)
db.session.commit()

# add sample users
sample_users = [
    {
        "username": "stgibson",
        "email": "stgibson@ucsc.edu",
        "password": "password",
        "city_id": cities[0].id
    },
    {
        "username": "seangibson",
        "email": "seangibson@comcast.net",
        "password": "password",
        "city_id": cities[0].id
    },
    {
        "username": "johndoe",
        "email": "johndoe@gmail.com",
        "password": "password",
        "city_id": cities[1].id
    },
    {
        "username": "frankie",
        "email": "fsinatra@comcast.net",
        "password": "password",
        "city_id": cities[2].id
    },
    {
        "username": "davidlean",
        "email": "dvdlean@gmail.com",
        "password": "password",
        "city_id": cities[3].id
    }
]
users = [User.signup(user["username"], user["email"], user["password"], \
    user["city_id"]) for user in sample_users]
db.session.add_all(users)
db.session.commit()

# add sample species
sample_species = [
    {
        "name": "loxodonta africana",
        "threatened": "VU"
    },
    {
        "name": "canis lupus",
        "threatened": "LC"
    },
    {
        "name": "acinonyx jubatus",
        "threatened": "VU"
    },
    {
        "name": "panthera tigris",
        "threatened": "EN"
    },
    {
        "name": "gorilla beringei",
        "threatened": "CR"
    }
]
species = [Species(name=species["name"], threatened=species["threatened"]) \
    for species in sample_species]
db.session.add_all(species)
db.session.commit()

# add sample users_species
sample_users_species = [
    {
        "user_id": users[0].id,
        "species_id": species[0].id
    },
    {
        "user_id": users[0].id,
        "species_id": species[1].id
    },
    {
        "user_id": users[1].id,
        "species_id": species[1].id
    },
    {
        "user_id": users[2].id,
        "species_id": species[1].id
    },
    {
        "user_id": users[2].id,
        "species_id": species[2].id
    },
    {
        "user_id": users[3].id,
        "species_id": species[3].id
    },
    {
        "user_id": users[4].id,
        "species_id": species[3].id
    },
    {
        "user_id": users[4].id,
        "species_id": species[4].id
    }
]
users_species = [User_Species(user_id=user_species["user_id"], \
    species_id=user_species["species_id"]) for user_species in \
    sample_users_species]
db.session.add_all(users_species)
db.session.commit()

# add sample species_countries
sample_species_countries = [
    {
        "species_id": species[0].id,
        "country_id": countries[0].id
    },
    {
        "species_id": species[1].id,
        "country_id": countries[0].id
    },
    {
        "species_id": species[1].id,
        "country_id": countries[1].id
    },
    {
        "species_id": species[2].id,
        "country_id": countries[0].id
    },
    {
        "species_id": species[2].id,
        "country_id": countries[2].id
    },
    {
        "species_id": species[3].id,
        "country_id": countries[2].id
    },
    {
        "species_id": species[4].id,
        "country_id": countries[0].id
    },
    {
        "species_id": species[4].id,
        "country_id": countries[1].id
    },
    {
        "species_id": species[4].id,
        "country_id": countries[2].id
    }
]
species_countries = \
    [Species_Country(species_id=species_country["species_id"], \
    country_id=species_country["country_id"]) for species_country in \
    sample_species_countries]
db.session.add_all(species_countries)
db.session.commit()