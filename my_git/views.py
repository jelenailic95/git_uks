# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import messages
from my_git.forms import UserRegisterForm, LoginForm
from my_git.models import User
from my_git.constants import HttpMethod


def welcome(request):
    return render(request, 'my_git/welcome.html')


def home(request):
    return render(request, 'my_git/home.html')


def login(request):
    print(request.method)
    if request.method == HttpMethod.POST.name:
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                result = User.objects.get(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
                print(result)
                return redirect('home')
            except User.DoesNotExist:
                messages.error(request, 'Bad credentials, try to login now!')
                return redirect('login')
    else:
        form = LoginForm()
    return render(request, 'my_git/users/login.html', {'form': form})


def register(request):
    if request.method == HttpMethod.POST.name:
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
