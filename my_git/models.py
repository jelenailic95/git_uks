from django.db import models

from datetime import datetime


# Create your models here.


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(default='', max_length=100)
    email = models.EmailField(default=1)
    password = models.CharField(max_length=30)

    def __str__(self):
        return "{}".format(self.username)


class Repository(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # cascade ili null
    contributors = models.ManyToManyField(User, related_name='contributors')
    TYPE_OPTION = (
        ('public', 'public'),
        ('private', 'private'))
    type = models.CharField(choices=TYPE_OPTION, max_length=7, default='public')
    creation_date = models.DateTimeField(default=datetime.now)
    language = models.CharField(default='', max_length=150)
    star = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.name)

    def __str__(self):
        return "{}".format(self.name)


class Milestone(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    due_date = models.DateField()
    open = models.BooleanField()
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.title)


class Label(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=15)

    def __str__(self):
        return "{}".format(self.name)


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    open = models.BooleanField()
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.title)


class Issue(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=400)
    date = models.DateTimeField()
    open = models.BooleanField()
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, blank=True)
    label = models.ManyToManyField(Label)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assignees = models.ManyToManyField(User, related_name='assignee')

    def __str__(self):
        return "{}".format(self.title)

    def save_new_issue(title, content, milestone, labels, logged_user, assignees):
        issue = Issue()
        issue.date = datetime.now()
        issue.open = True
        issue.title = title
        issue.content = content
        issue.milestone = Milestone.objects.get(title=milestone)
        issue.user = User.objects.get(username=logged_user)
        issue.save()
        for label in labels:
            issue.label.add(Label.objects.get(name=label))
        for un in assignees:
            issue.assignees.add(User.objects.get(username=un))
        issue.save()


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=400)
    date = models.DateTimeField()
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)


class HistoryItem(models.Model):
    id = models.AutoField(primary_key=True)
    old_value = models.CharField(max_length=500)
    new_value = models.CharField(max_length=500)
    attr_name = models.CharField(max_length=500)
    datetime = models.DateTimeField()
    MODE_OPTION = (
        ('create', 'create'),
        ('change', 'change'))
    mode = models.CharField(choices=MODE_OPTION, max_length=6, default='create')
