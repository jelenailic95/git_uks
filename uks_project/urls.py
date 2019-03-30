"""uks_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from my_git import views as my_git_views
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', my_git_views.welcome, name='welcome'),
    path('home/', my_git_views.home, name='home'),
    # todo: change auth_views to my_git_views.login
    path('login/', auth_views.LoginView.as_view(template_name='my_git/users/login.html'), name='login'),
    path('logout/', auth_views.LoginView.as_view(template_name='my_git/users/logout.html'), name='logout'),
    path('register/', my_git_views.register, name='register')
]

urlpatterns += staticfiles_urlpatterns()