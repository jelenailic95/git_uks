# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages

from my_git.constants import HttpMethod
from my_git.forms import UserRegisterForm, LoginForm, UserUpdateProfileForm
from my_git.models import User
from my_git.constants import HttpMethod


def welcome(request):
    # del request.session['user']
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

                # set logged user
                request.session['user'] = result.username
                return redirect('home')
            except User.DoesNotExist:
                messages.error(request, 'Bad credentials, try again!')
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


def get_user_profile(request):
    # request.user
    username = User.objects.get(username=request.session['user'])
    logged_user = User.objects.get(username=username)

    return render(request, 'my_git/users/user_profile.html', {"user": logged_user})


def update_user_profile(request):
    username = User.objects.get(username=request.session['user'])
    logged_user = User.objects.get(username=username)

    if request.method == 'POST':
        form = UserUpdateProfileForm(request.POST)
        if form.is_valid():
            logged_user.username = form.cleaned_data['username']
            request.session['user'] = logged_user.username

            # if password is changed set the new one
            if form.cleaned_data['password'] != "":
                logged_user.password = form.cleaned_data['password']

            logged_user.email =  form.cleaned_data['email']
            logged_user.save()

            messages.success(request, 'Your profile has been successfully saved!')
            return  render(request, 'my_git/users/user_profile.html', {"user": logged_user})
    else:
        form = UserUpdateProfileForm()

    # fill the form with the user data
    form.initial['username'] = logged_user.username
    form.initial['email'] = logged_user.email

    context = {
        'form': form
    }

    return render(request, 'my_git/users/update_user_profile.html', context)
