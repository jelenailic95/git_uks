# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
import logging
from my_git.constants import HttpMethod
from my_git.forms import UserRegisterForm, LoginForm
from my_git.models import User, Issue, Label


def welcome(request):
    return render(request, 'my_git/welcome.html')


def home(request):
    context = {"home_view": "active"}
    return render(request, 'my_git/home.html', context)


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


def issues_view(request):
    issues = Issue.objects.all()
    print(issues[0].open)
    context = {
        "issues_view": "active",
        "num_of_open": 0,
        "num_of_closed": 0,
        'issues': issues
    }
    return render(request, 'my_git/issues/issues.html', context)


def new_issue(request):
    labels = Label.objects.all()
    if request.method == HttpMethod.POST.name:
        pass
    else:
        pass
    context = {'user': request.user}
    return render(request, 'my_git/issues/new_issue.html', context)
