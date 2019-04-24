import random
import string

from django.db import models

from datetime import datetime


# Create your models here.
def upload_location(instance, filename):
    return "%s/%s" % (instance.id, filename)


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(default='', max_length=100)
    email = models.EmailField(default=1)
    password = models.CharField(max_length=30)
    image = models.ImageField(upload_to=upload_location, null=True, blank=True, default='')

    def __str__(self):
        return "{}".format(self.username)


class Repository(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # cascade ili null
    collaborators = models.ManyToManyField(User, related_name='collaborators')
    TYPE_OPTION = (
        ('public', 'public'),
        ('private', 'private'))
    type = models.CharField(choices=TYPE_OPTION, max_length=7, default='public')
    creation_date = models.DateTimeField(default=datetime.now)
    language = models.CharField(default='', max_length=150)
    star = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.name)


class Wiki(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=5000)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.title)


class Milestone(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, default='')
    description = models.CharField(max_length=500, null=True, default='')
    due_date = models.DateField()
    closed_date = models.DateField(null=True)
    open = models.BooleanField(default=True)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.title)

    @staticmethod
    def find_milestones_by_repository(repo):
        try:
            return Milestone.objects.filter(repository_id=repo)
        except Milestone.DoesNotExist:
            return None

    @staticmethod
    def find_milestone_by_name_and_repo(repo, name):
        try:
            return Milestone.objects.get(repository_id=repo, title=name)
        except Milestone.DoesNotExist:
            return None

    @staticmethod
    def save_new_milestone(title, description, date, open, rep):
        print(open)
        print(rep.name)
        milestone = Milestone()
        milestone.title = title
        milestone.description = description
        milestone.due_date = date
        milestone.open = open
        milestone.repository = rep
        Milestone.save(milestone)


class Label(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=15)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return "{}".format(self.name)

    def save_new_label(name, description, color):
        label = Label()
        label.name = name
        label.description = description
        label.color = color
        label.save()


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
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return "{}".format(self.title)

    def save_new_issue(title, content, milestone, labels, logged_user, assignees, repository):
        issue = Issue()
        issue.date = datetime.now()
        issue.open = True
        issue.title = title
        issue.content = content
        issue.milestone = Milestone.find_milestone_by_name_and_repo(repo=repository.id, name=milestone)
        issue.user = User.objects.get(username=logged_user)
        issue.repository = repository
        issue.save()
        for label in labels:
            issue.label.add(Label.objects.get(name=label))
        for un in assignees:
            issue.assignees.add(User.objects.get(username=un))

    @staticmethod
    def find_issues_by_repository(repo):
        try:
            return Issue.objects.filter(repository_id=repo)
        except Issue.DoesNotExist:
            return None

    @staticmethod
    def update_issue(issue, assignees, labels, milestone, repository):
        issue_for_update = issue
        issue_for_update.milestone = Milestone.find_milestone_by_name_and_repo(repo=repository.id, name=milestone)
        issue_for_update.save()
        issue.assignees.clear()
        issue.label.clear()
        for label in labels:
            issue.label.add(Label.objects.get(name=label))
        for un in assignees:
            issue.assignees.add(User.objects.get(username=un))


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=400)
    date = models.DateTimeField()
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    @staticmethod
    def find_comments_by_issue_id(issue_id):
        try:
            return Comment.objects.filter(issue_id=issue_id).order_by('date')
        except Comment.DoesNotExist:
            return None

    @staticmethod
    def save_comment(content, user, issue):
        comment = Comment()
        comment.content = content
        comment.date = datetime.now()
        comment.author = User.objects.get(username=user)
        comment.issue = issue
        comment.save()


class HistoryItem(models.Model):
    id = models.AutoField(primary_key=True)
    old_value = models.CharField(max_length=500)
    new_value = models.CharField(max_length=500)
    attr_name = models.CharField(max_length=500)
    date = models.DateTimeField()
    MODE_OPTION = (
        ('create', 'create'),
        ('change', 'change'))
    mode = models.CharField(choices=MODE_OPTION, max_length=6, default='create')
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, default=None)

    @staticmethod
    def save_history_item(issue, old_value, new_value, attr_name, mode, author):
        history_item = HistoryItem()
        history_item.issue = issue
        history_item.old_value = old_value
        history_item.new_value = new_value
        history_item.attr_name = attr_name
        history_item.date = datetime.now()
        history_item.mode = mode
        history_item.author = author
        history_item.save()


class Commit(models.Model):
    id = models.AutoField(primary_key=True)
    commit_id = models.CharField(max_length=100, default='')
    message = models.CharField(max_length=100, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    date = models.DateField(null=True)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return "{}".format(self.message)

    @staticmethod
    def create_new_commit(message, repository, user):
        commit = Commit()
        commit.message = message
        commit.repository = repository
        commit.user = user
        commit.date = datetime.now()
        commit.commit_id = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
        Commit.save(commit)

    @staticmethod
    def find_commits_by_repository(repo):
        try:
            return Commit.objects.filter(repository_id=repo)
        except Commit.DoesNotExist:
            return None


class Branch(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    date = models.DateField(null=True)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return "{}".format(self.name)

    @staticmethod
    def create_new_branch(name, repository, user):
        branch = Branch()
        branch.name = name
        branch.repository = repository
        branch.user = user
        branch.date = datetime.now()
        Branch.save(branch)

    @staticmethod
    def find_branches_by_repository(repo):
        try:
            return Branch.objects.filter(repository_id=repo)
        except Branch.DoesNotExist:
            return None
