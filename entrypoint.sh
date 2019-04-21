#!/bin/bash

# collect static files
python manage.py collectstatic --noinput

# create migrations
python manage.py makemigrations

# apply migrations
python manage.py migrate

# start server
python manage.py runserver 0.0.0.0:8000