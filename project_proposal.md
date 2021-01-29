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
* Logged in users can search for a species to learn about its threatened level
* Logged in users can choose to add a threatened species to their list of
species
* Logged in users can remove a threatened species from their list of species
* If a certain number of users in the same city share a species in their lists
of species, they are all notified and will be able to share their contact
information with each other
* New users must check a box acknowledging that they understand that by using
the site, other users may become aware of the user's username, email, and
approximate location
* There are instructions on how to use the website in the about page
* Users can only search for a species in their country
* Users are notified via email when the correct number of users in the same city
like the same species
* Logged in users can view and modify their profile
* Logged in users users can delete their accounts
* Users select country from a dropdown when signing up or editing their profile

### User Flow
If the user is visiting the website for the first time, the user must first
create an account by entering a username, an email address, the city and country
the user lives in, and a password. If the user already has an account, the user
must login using the same username and password the user used to create an
account. The user may search for a species by name, and if the species exists
and is in the country the user is in, the user gets information on its
threatened level. If the species is not found or is not in the country the user
is in, the user instead gets a message letting the user know why they can't
access the species data. If the user does get information on the species, the
user also sees a button that when clicked, will add the species to a list of
species. The user can also choose to remove a species from the list. If a
certain number of users in the same city have the same species in their lists as
a species in the user's list, the user an email of the other users in the user's
city that have added the species to their lists. While logged in, the user may
also edit or delete the user's profile. When the user is done working on the
website for the time being, the user may logout. Users may always access the
about page to get information on how to use the website, whether or not they
are logged in.

### Backlog

The following is a list of backlog features for future versions of the project:
* Add error handling for routes
* Add a contact us page
* Alphabetize country names for dropdown for users to sign up
* Also display common name(s) for species to user
* Make threatened level name more user friendly
* The user can choose to be notified of other users based on county, state, or a
specified radius from the user's location
* The user's species list will update if the user edits country in the user's
profile
* The user can also input a state or province, based on their country
* Set up email server separate from personal email address to send emails to
users
* When users search for species, they only need to type part of the species'
name
* When users are notified of each other, they can create a joint document to
store contact information or create a plan for helping their mutual species
* When searching for a species, the user can use a non-scientific name, such as
dog or cat
