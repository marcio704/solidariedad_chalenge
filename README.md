INSTALLATION
============

Clone project:

`$ git clone git@github.com:marcio704/solidariedad_chalenge.git`

`$ cd solidaridad`


Create virtualenv and install dependencies:

`$ virtualenv /the/path/you/want/venv -p python3.5`

`$ source /the/path/you/want/venv/bin/activate`

`$ pip install -r requirements.txt`

Run app locally:

`python manage.py runserver localhost:8000`

In case you want to log on Django Admin, there's a default admin user already created:

URL: http://localhost:8000/admin

User: admin

Password: mgderune2k



TESTS
=====

`$ cd solidaridad`

`$ source /the/path/you/want/venv/bin/activate`

`$ python manage.py test`


POSTMAN
=======

There is a Postman collection on project root called "Solidariedad.postman_collection",
download it in case you want to test all API entries via Postman.

That should be enough :)