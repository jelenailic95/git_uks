# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
import logging
from my_git.constants import HttpMethod
from my_git.forms import *
from my_git.models import User, Issue, Label, Repository, Milestone, Comment


def welcome(request):
    # del request.session['user']
    return render(request, 'my_git/welcome.html')


def home(request):
    context = {"home_view": "active"}
    return render(request, 'my_git/home.html', context)


def login(request):
    if request.method == HttpMethod.POST.name:
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                result = User.objects.get(email=form.cleaned_data['email'], password=form.cleaned_data['password'])

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
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            obj = User()
            obj.username = form.cleaned_data['username']
            obj.password = form.cleaned_data['password1']
            obj.email = form.cleaned_data['email']
            print(request.FILES)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
                print(obj.image)
                print(request.FILES['image'])

            obj.save()
            messages.success(request, 'Account successfully created! Log in now!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'my_git/users/register.html', {'form': form})


def get_user_profile(request):
    # request.user
    logged_user = get_logged_user(request.session['user'])

    return render(request, 'my_git/users/user_profile.html', {"user": logged_user})


def update_user_profile(request):
    logged_user = get_logged_user(request.session['user'])
    if request.method == HttpMethod.POST.name and 'username' in request.POST:
        form = UserUpdateProfileForm(request.POST, request.FILES)
        if form.is_valid():
            logged_user.username = form.cleaned_data['username']
            request.session['user'] = logged_user.username

            # if password is changed set the new one
            if form.cleaned_data['password'] != "":
                logged_user.password = form.cleaned_data['password']

            logged_user.email = form.cleaned_data['email']

            if 'image' in request.FILES:
                logged_user.image = request.FILES['image']

            logged_user.save()

            messages.success(request, 'Your profile has been successfully saved!')
            return render(request, 'my_git/users/user_profile.html', {"user": logged_user})
    else:
        form = UserUpdateProfileForm()

    # fill the form with the user data
    form.initial['username'] = logged_user.username
    form.initial['email'] = logged_user.email

    context = {
        'form': form
    }

    return render(request, 'my_git/users/update_user_profile.html', context)


def issues_view(request, repo_name):
    repository = Repository.objects.get(name=repo_name)
    issues = Issue.find_issues_by_repository(repo=repository.id)
    milestones = Milestone.find_milestones_by_repository(repo=repository.id)
    labels = Label.objects.all()
    print(request.GET.get('query'))
    if request.GET.get('open'):
        issues = issues.filter(open=True)
    elif request.GET.get('closed'):
        issues = issues.filter(open=False)
    elif request.GET.get('query'):
        issues = issues.filter(title__contains=request.GET.get('query'))
    context = {
        "issues_view": "active",
        "num_of_open": issues.filter(open=True).count(),
        "num_of_closed": issues.filter(open=False).count(),
        "issues": issues,
        "labels": labels,
        "milestones": milestones,
        "repository": repository,
        "owner": repository.owner,
    }

    if request.method == HttpMethod.POST.name:
        open_issue_sort = request.POST.get('open_issue_sort')
        closed_issue_sort = request.POST.get('closed_issue_sort')
        title_sort_up = request.POST.get('title_sort_up')
        title_sort_down = request.POST.get('title_sort_down')
        milestones_sort_up = request.POST.get('milestones_sort_up')
        milestones_sort_down = request.POST.get('milestones_sort_down')

        open_issue_filter = request.POST.get('open_issues_filter')
        closed_issue_filter = request.POST.get('closed_issues_filter')

        '''
        if open_issue_filter:
            context['issues'] = issues.filter(open=True)
            context['num_of_open'] = issues.filter(open=True).count()
            context['num_of_closed'] = 0
        elif closed_issue_filter:
            context['issues'] = issues.filter(open=False)
            context['num_of_open'] = 0
            context['num_of_closed'] = issues.filter(open=False).count()
        '''

        if open_issue_sort:
            context['issues'] = issues.order_by('-open')
        elif closed_issue_sort:
            context['issues'] = issues.order_by('open')
        elif title_sort_up:
            context['issues'] = issues.order_by('-title')
        elif title_sort_down:
            context['issues'] = issues.order_by('title')
        elif milestones_sort_up:
            context['issues'] = issues.order_by('milestone')
        elif milestones_sort_down:
            context['issues'] = issues.order_by('-milestone')

    return render(request, 'my_git/issues/issues.html', context)


def new_issue(request, repo_name):
    repository = Repository.objects.get(name=repo_name)
    labels = Label.objects.all()
    milestones = Milestone.find_milestones_by_repository(repo=repository.id)

    username = User.objects.get(username=request.session['user'])

    context = {
        'user': username,
        'repository': repository,
        'owner': repository.owner,
        'collaborators': repository.collaborators.all(),
        'labels': labels,
        'milestones': milestones,
        "issues_view": "active",
    }

    if request.method == HttpMethod.POST.name:
        assignee_form = request.POST.getlist('assignee')
        labels_form = request.POST.getlist('labels')
        title_form = request.POST.get('titleInput')
        content_form = request.POST.get('contentInput')
        milestone_form = request.POST.get('milestone')
        Issue.save_new_issue(title=title_form, content=content_form, milestone=milestone_form,
                             labels=labels_form,
                             logged_user=username, assignees=assignee_form, repository=repository)
        return redirect('issues', repo_name=repository)
    else:
        return render(request, 'my_git/issues/new_issue.html', context)


def issue_view(request, repo_name, id):
    logged_user = get_logged_user(request.session['user'])
    repository = Repository.objects.get(name=repo_name)
    issue = Issue.objects.get(id=id)
    milestones = Milestone.find_milestones_by_repository(repo=repository.id)
    comments = Comment.find_comments_by_issue_id(issue_id=issue.id)
    context = {
        'issue': issue,
        'repository': repository,
        "issues_view": "active",
        "comments": comments,
        "owner": repository.owner,
        "selected_milestone": [issue.milestone],
        "milestones": milestones,
        "assignes": issue.assignees.all(),
        'collaborators': repository.collaborators.all(),
        'all_labels': Label.objects.all()
    }

    if request.method == HttpMethod.POST.name:
        close_button = request.POST.get('closeBtn')
        reopen_button = request.POST.get('reopenBtn')
        save_button = request.POST.get('saveChangesBtn')
        if close_button:
            issue.open = False
            issue.save()
        elif reopen_button:
            issue.open = True
            issue.save()
        elif save_button:
            assignee_form = request.POST.getlist('assignee')
            print(assignee_form)
            labels_form = request.POST.getlist('labels')
            milestone_form = request.POST.get('milestone')
            Issue.update_issue(issue=issue, assignees=assignee_form, labels=labels_form, milestone=milestone_form,
                               repository=repository)
        else:
            comment_for_save = request.POST.get('comment')
            Comment.save_comment(comment_for_save, logged_user, issue)

    return render(request, 'my_git/issues/issue_view.html', context)


def get_repositories(request):
    logged_user = get_logged_user(request.session['user'])

    repositories = Repository.objects.all().order_by('-creation_date')

    # filter repositories by name
    if request.method == 'GET' and 'repo_name' in request.GET:
        name = request.GET.get('repo_name', '')

        # filter by case insensitive repository name
        repositories = Repository.objects.filter(name__icontains=name).order_by('-creation_date')

    if request.method == HttpMethod.POST.name:
        repository = Repository.objects.get(id=request.POST.get('repo_id'))
        repository.star = request.POST.get('repo_star')
        repository.save()

    context = {
        "user": logged_user,
        "repositories": repositories,
        "repositories_view": "active"
    }

    return render(request, 'my_git/repositories/repositories.html', context)


def get_stars(request):
    repositories = Repository.objects.filter(star=True).order_by('-creation_date')

    # filter repositories by name
    if request.method == 'GET' and 'repo_name' in request.GET:
        name = request.GET.get('repo_name', '')

        # filter by case insensitive repository name
        repositories = repositories.filter(name__icontains=name).order_by('-creation_date')

    if request.method == HttpMethod.POST.name:
        repository = Repository.objects.get(id=request.POST.get('repo_id'))
        repository.star = request.POST.get('repo_star')
        repository.save()

    context = {
        'repositories': repositories,
        'stars_view': 'active'
    }

    return render(request, 'my_git/stars.html', context)


def get_repository(request, repo_name):
    repository = Repository.objects.get(name=repo_name)

    context = {
        "repository": repository,
        "owner": repository.owner,
        "repository_view": "active"
    }

    return render(request, 'my_git/repositories/repository_preview.html', context)


def create_repository(request):
    logged_user = get_logged_user(request.session['user'])

    if request.method == HttpMethod.POST.name:
        form = CreateRepositoryForm(request.POST)
        if form.is_valid():
            obj = Repository()
            obj.name = form.cleaned_data['repository_name']
            obj.description = form.cleaned_data['description']
            obj.type = form.cleaned_data['type']
            obj.owner = logged_user
            obj.save()
            messages.success(request, 'Repository is successfully created!')
            return redirect('repositories')
    else:
        form = CreateRepositoryForm()

    context = {
        'owner': logged_user.username,
        'form': form
    }

    return render(request, 'my_git/repositories/create_repository.html', context)


def get_repository_settings(request, repo_name):
    repository = Repository.objects.get(name=repo_name)

    # rename repository
    if request.method == HttpMethod.POST.name and 'btn-rename' in request.POST:
        form = InputFieldForm(request.POST)
        if form.is_valid():
            repository.name = form.cleaned_data['value']
            repository.save()
            messages.success(request, 'Repository is successfully renamed.')
            return redirect('repositories')
    else:
        form = InputFieldForm()

    # add collaborator
    if request.method == HttpMethod.POST.name and 'btn-add-collaborator' in request.POST:
        add_collaborator(request, repository)

    # remove collaborator
    if request.method == HttpMethod.POST.name and 'remove-collaborator' in request.POST:
        collaborator_id = request.POST.get('collaborator_id')
        repository.collaborators.remove(User.objects.get(id=collaborator_id))
        repository.save()

    # delete repository
    if request.method == HttpMethod.POST.name and 'btn-delete' in request.POST:
        form = DeleteForm(request.POST)
        if form.is_valid():
            repository.delete()
            messages.success(request, 'Repository is successfully deleted!')
            return redirect('repositories')

    form.initial['value'] = repository.name

    context = {
        "repository": repository,
        "owner": repository.owner,
        "form_update": form,
        "repository_settings_view": "active",
        "collaborators": repository.collaborators
    }

    return render(request, 'my_git/repositories/repository_settings.html', context)


def add_collaborator(request, repository):
    username = request.POST.get('collaborator')
    try:
        collaborator = User.objects.get(username=username)
        print(username)
        if collaborator == repository.owner or collaborator in repository.collaborators.all():
            messages.warning(request, 'Already a collaborator. Add someone new.')
        else:
            repository.collaborators.add(collaborator)
            repository.save()
            messages.success(request, 'Collaborator is successfully added.')
    except User.DoesNotExist:
        messages.warning(request, 'User with this username doesn\'t exist. Try again!')


def get_logged_user(username):
    logged_user = User.objects.get(username=username)
    return logged_user
