from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


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
