import os
from typing import TypeVar

UserOrNone = TypeVar("UserOrNone", User, None)
MATCH_NUM = int(os.environ.get("MATCH_NUM", 10))

def create_user(
    username: str,
    email: str,
    password: str,
    city: str,
    country: str
) -> UserOrNone:
    """
        Creates new user with given credentials. If successful, returns new
        user, otherwise returns None.
        :type username: str
        :type email: str
        :type password: str
        :type city: str
        :type country: str
        :rtype: User | None
    """

    country_code = country
    city_name = city
    country_id = None
    city_id = None

    # country must be in db cause selected by user
    country = Country.query.filter_by(code=country_code).one()
    country_id = country.id

    city = City.query.filter_by(name=city_name).one_or_none()
    # if the city is in db, get its id
    if city:
        city_id = city.id
    # otherwise, add city to db
    else:
        city = City(name=city_name, country_id=country_id)
        db.session.add(city)
        db.session.commit()
        city_id = city.id

    # add user to db
    return User.signup(username, email, password, city_id)

def edit_profile(user_id: int, username: str, email: str, city: str, country: str) -> None:
    """
        Edits profile of user with id user_id
        :type user_id: in
        :type username: str
        :type email: str
        :type city: str
        :type country: str
    """

    user = User.query.get(user_id)
    user.username = username
    user.email = email
    db.session.add(user)
    db.session.commit()

    country_code = country
    city_name = city
    country_id =  None
    city_id = None
    if user.city.country.code == country_code:
        country_id = user.city.country.id
    if user.city.name == city_name:
        city_id = user.city.id

    if country_id:
        country = Country.query.get(country_id)
        # if city has changed, check if in country
        if not city_id:
            city_id_list = [city.id for city in country.cities if \
                city.name == city_name]
            if city_id_list:
                # should only be 1 city with that name in the country
                city_id = city_id_list[0]
                user.city_id = city_id
                db.session.add(user)
                db.session.commit()
            # otherwise need to add city to db
            else:
                city = City(name=city_name, country_id=country_id)
                db.session.add(city)
                db.session.commit()
                city_id = city.id
                user.city_id = city_id
                db.session.add(user)
                db.session.commit()
    # if country has changed, get new country and city
    else:
        country = Country.query.filter_by(code=country_code).one()
        country_id = country.id
        # even if city hasn't changed, since in different country, need to add
        city = City(name=city_name, country_id=country_id)
        db.session.add(city)
        db.session.commit()
        city_id = city.id
        user.city_id = city_id
        db.session.add(user)
        db.session.commit()

def is_match(species_id: int, city_id: int) -> bool:
    """
        If MATCH_NUM users in city with id city_id like species with id
        species_id, returns True, otherwise returns False
        :type species_id: int
        :type city_id: int
        :rtype: bool
    """

    city = City.query.get(city_id)
    num_of_users = 0
    # count number of users in city that have species with id species.id
    for user in city.users:
        for species in user.species:
            if species.id == species_id:
                num_of_users += 1
    result = num_of_users == MATCH_NUM
    return result

def make_notification(species_id: int, user_id: int) -> str:
    """
        Generate message that shares all users other than user with id user_id
        who have species with id species_id in their list, that are in the same
        city as user with id user_id
        :type species_id: int
        :type user_id: int
        :rtype: str
    """

    user = User.query.get(user_id)
    species = Species.query.get(species_id)
    city_id = user.city_id
    notification = \
        f"Congratulations! You and {MATCH_NUM - 1} other people in \
{user.city.name}, {user.city.country.name} have {species.name} in their \
lists!  Here is a list of the other users:"
    # add users other than user with id user_id in city with id city_id to list
    for user in species.users:
        if user.city_id == city_id and user.id != user_id:
            notification += f"\n{user.username} ({user.email})"
    return notification