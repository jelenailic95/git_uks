# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages

from my_git.constants import HttpMethod
from my_git.forms import UserRegisterForm
from my_git.models import User


def home(request):
    return render(request, 'my_git/home.html')


def login(request):
    if request.method == HttpMethod.POST:
        form = UserCreationForm(request.POST)
        print('POST')
        result = User.objects.get(username=form.cleand_data['username'], password=form.cleand_data['password'])
        if result is None:
            messages.error(request, 'Bad credentials, try to login again!')
    return render(request, 'my_git/users/login.html')


def register(request):
    if request.method == HttpMethod.POST:
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            obj = User()
            obj.username = form.cleaned_data['username']
            obj.password = form.cleaned_data['password1']
            obj.email = form.cleaned_data['email']
            obj.save()
            messages.success(request, 'Account successfully created! Log in now!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'my_git/users/register.html', {'form': form})
