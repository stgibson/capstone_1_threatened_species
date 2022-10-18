# capstone_1_threatened_species

## Website Title
[Threatened Species](https://threatened-species.herokuapp.com)

## Website Description
This website allows users to locate other users in their vicinity who share a
passion for protecting a certain threatened species. The way that the website
has been implemented thus far, when a certain number of users in the same city
add the same species to their list of favorite species, they all receive an
email notifying them of each other's usernames and email addresses they used to
create an account.

## Features Implemented
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
* Logged in users can delete their accounts
* Users select country from a dropdown when signing up or editing their profile

## User Flow
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
certain number of users in the same city have the same species in their lists,
the last user to add the species to the user's list will receive an email
containing the other users' usernames and email addresses. While logged in,
the user may also edit or delete the user's profile. When the user is done
working on the website for the time being, the user may logout. Users may
always access the about page to get information on how to use the website,
whether or not they are logged in.

## API Link
[API link](https://apiv3.iucnredlist.org/api/v3/docs)

## Technology Stack
* Python
* Flask
* PostgreSQL
* SQLAlchemy
* Jinja
* WTForms
* Bootstrap
* Heroku
