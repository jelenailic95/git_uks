from django.db import models

# Create your models here.


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=50)
    email = models.EmailField(default=1)


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1)   # cascade ili null
    contributors = models.ManyToManyField(User, related_name='contributors')


class Milestone(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    due_date = models.DateField()
    open = models.BooleanField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Label(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=15)


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    open = models.BooleanField()
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    user = models.ForeignKey(User,  on_delete=models.CASCADE)


class Issue(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=400)
    date = models.DateTimeField()
    open = models.BooleanField()
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    label = models.ManyToManyField(Label)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


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
