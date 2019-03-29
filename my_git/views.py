# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import messages
from my_git.forms import UserRegisterForm


def welcome(request):
    return render(request, 'my_git/welcome.html')

def home(request):
    return render(request, 'my_git/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # email = form.cleaned_data.get('email')
            messages.success(request, 'Account successfully created! Log in now!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'my_git/users/register.html', {'form':form})

