import itertools

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from my_git.models import Label, Repository


class UserRegisterForm(UserCreationForm):
    username = forms.CharField()
    email = forms.EmailField()
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    # nested namespace for config
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    class Meta:
        fields = ['email', 'password']


class UserUpdateProfileForm(forms.ModelForm):
    username = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    password = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class CreateRepositoryForm(forms.ModelForm):
    repository_name = forms.CharField()
    description = forms.CharField(required=False)
    type = forms.CharField()

    class Meta:
        model = Repository
        fields = ['repository_name', 'description', 'type']


class DeleteForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = []


class UpdateNameForm(forms.ModelForm):
    repository_name = forms.CharField(label='')

    class Meta:
        model = Repository
        fields = ['repository_name']
