#!/bin/bash

# create migrations
python manage.py makemigrations

# apply migrations
python manage.py migrate

# create super user
python manage.py createsuperuser --username admin --email admin@example.com --noinput
python manage.py changepassword admin
# start server
python manage.py runserver 0.0.0.0:8000