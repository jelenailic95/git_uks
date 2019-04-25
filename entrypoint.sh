#!/bin/bash

# create migrations
python manage.py makemigrations

# apply migrations
python manage.py migrate

# create super user
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'mdj1646MDJ')"
# start server
python manage.py runserver 0.0.0.0:8000