from django.apps import apps
from django.contrib import admin

# Register your models here.
from my_git.models import *

for model in apps.get_app_config('my_git').models.values():
    admin.site.register(model)
