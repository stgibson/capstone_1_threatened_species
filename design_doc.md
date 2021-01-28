# Design Document

## Files
* templates/
  * about.html  
    Jinja template to display the about page

  * base.html  
    Base Jinja template for all other templates to inherit from

  * edit.html  
    Jinja template to display the edit page

  * form.html  
    Jinja template that displays a WTForm, included in other templates that
    use forms

  * home.html  
    Jinja template that displays the home page

  * login.html  
    Jinja template that displays the login page

  * signup.html  
    Jinja template that displays the signup page

* .gitignore  
  Includes list of files that Git should not track

* acknowledgements.txt  
  Contains acknowledgements to websites I used to build the app

* app.py  
  Creates routes for the app with Flask

* database_schema.pdf  
  Screenshot of a Google Spreadsheet of the design for the database

* forms.py  
  Contains templates for WTForms

* helpers.py  
  Contains helper functions for the route functions in app.py

* models.py  
  Defines the models used for the database

* Procfile  
  Contains instructions for Heroku to deploy the app

* project_proposal.md  
  Original project proposal document

* README.md  
  Document that describes the app and how to use it

* requirements.txt  
  Contains a list of the required packages to run the app

* runtime.txt
  Contains the Python version number to use for the app

* seed.py  
  Creates all tables, and has commented out sample code for testing in
  development mode

* test_country_model.py  
  Tests Country model and its methods

* test_flask.py  
  Tests Flask routes

* test_helpers.py  
  Tests helper functions in helpers.py

* test_species_model.py  
  Tests Species model and its methods

* test_user_model.py  
  Tests User model and its methods