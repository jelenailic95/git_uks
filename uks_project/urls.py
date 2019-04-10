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
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', my_git_views.welcome, name='welcome'),
    path('home/', my_git_views.home, name='home'),
    # todo: change auth_views to my_git_views.login
    path('login/', my_git_views.login, name='login'),
    path('register/', my_git_views.register, name='register'),
    path('profile/', my_git_views.get_user_profile, name='profile_preview'),
    path('profile/edit', my_git_views.update_user_profile, name='profile_update'),
    path('repositories/', my_git_views.get_repositories, name='repositories'),
    path('repositories/<str:repo_name>', my_git_views.get_repository, name='repository_preview'),
    path('repositories/<str:repo_name>/settings', my_git_views.get_repository_settings, name='repository_settings'),
    path('repositories/<str:repo_name>/issues', my_git_views.issues_view, name='issues'),
    path('repositories/<str:repo_name>/issues/new', my_git_views.new_issue, name='new-issue'),
    path('new/', my_git_views.create_repository, name='create_repository'),
    path('stars/', my_git_views.get_stars, name='stars'),

]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
