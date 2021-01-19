# Capstone 1 Project Proposal

## Goal

The goal of this project is to create a website that allows users to locate
other users in their vicinity, who share a passion for protecting a certain
threatened species.

## Demographics

The target audience for this website is people who want to work with others to
help protect threatened species in their area and/or help to increase the
population of threatened species.

## API

The IUCN Red List API will be used for this project. This API allows servers to
request for information on the threatened level on a species. It allows for
looking up a species by its full species name, as well as for looking up a list
of species names in a given region. The regions in the API are based on specific
parts of a continent.

## Summary

### Database Schema

The database for the website will have models for users, species, cities, and
countries. The user model will include their username, email, encrypted
password, city, and a list of species. The species model will include its name,
its threatened level, the country it is in, and a list of users that have
selected it. The city model will have a name, the country that it's in, and a
list of users in the city. The country model will have a name, a list of cities
in the country, and a list of species in the country.

### Potential Issues

The API is free to use for noncommercial projects, however, I will need to make
a request for a token to use it.

### Sensitive Information

The server will need to protect the users' username, email, city, and
password. Since it uses the user's location to locate other nearby users, the
website will need to explicitly ask the user permission to let other users know
the user's approximate location.

### Minimum Viable Product

An MVP will have the following functionality:
* Users can sign up on the website by providing their username, email, city,
country, and password
* The server will encrypt passwords using bcrypt before storing it in the
database
* Users can login on the website with valid credentials (username and password)
* Logged in users can logout of their account on the website
* Logged in users can search for a species in their country to learn about its
threatened level
* Logged in users can choose to add a threatened species to their list of
species
* If a certain number of users in the same city share a species in their lists
of species, they are all notified and will be able to share their contact
information with each other

### User Flow

If the user is visiting the website for the first time, the user must first
create an account by entering a username, the user's email, the city and country
the user lives in, and a password. The user must also check a box acknowledging
that they understand that by using the site other users may become aware of the
user's username and the city the user lives in, if there is a match between
users. If the user already has an account, the user must login using the same
username and password the user used to create an account. The user may search
for a species by name, and if the species is located in the same country as the
user, the user gets information on the threatened level. If the species is not
found, the user gets a message stating that the species is not known by the
website. If the species is not found in the user's country, the user gets a
message stating that the species does not exist in the user's country. If the
user does get information on the species and the species is threatened, the user
also sees a button that when clicked, will add the species to a list of species.
The user can also choose to remove a species from the list. If a certain number
of users in the same city have the same species in their lists as a species in
the user's list, the user gets a list of the other users' usernames. The user
can then choose whether or not to send the user's email address to the other
users. When the user is done working on the website for the time being, the user
may logout. When the user is logged in, the user also has the option to delete
the user's account.

### Backlog

The following is a list of backlog features for future versions of the project:
* Instructions on how to use the website are provided
* Allow users to view and modify their profile
* Add an about page and contact us page
* Also display common name(s) for species to user
* Make threatened level name more user friendly
* User selects country from a dropdown
* The user can choose to be notified of other users based on county, state, or a
specified radius from the user's location
* The server will determine which country the user is in based on the city the
user is in
* The user can also input a state or province, based on their country
* When users are notified of each other, they can create a joint document to
store contact information or create a plan for helping their mutual species
* When searching for a species, the user can use a non-scientific name, such as
dog or cat
