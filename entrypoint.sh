#!/bin/bash

# create migrations
python manage.py makemigrations

# apply migrations
python manage.py migrate

# start server
python manage.py runserver 0.0.0.0:8000
