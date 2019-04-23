from django.test import TestCase, RequestFactory
from my_git.models import *
from my_git.views import *
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse


# Create your tests here.

class RepositoryTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="user", password="pass1", email="user@gmail.com")
        self.repository = Repository.objects.create(name="repo", description="desc", owner=self.user, type="private")
        session = self.client.session
        session['user'] = 'user'
        session.save()

    def test_create_repository(self):
        repository = Repository.objects.get(name="repo")

        self.assertIsInstance(repository, Repository)
        self.assertEqual(repository.name, "repo")
        self.assertEqual(repository.description, "desc")
        self.assertEqual(repository.owner, self.user)
        self.assertEqual(repository.type, "private")

    def test_get_repositories(self):
        response = self.client.get(reverse('repositories'))

        self.assertEqual(response.status_code, 200)

        # one repository is added in setUp
        self.assertEqual(len(response.context['repositories'].all()), 1)
        self.assertEqual(response.context['repositories'][0].name, 'repo')
        self.assertEqual(response.context['repositories'][0].description, 'desc')
        self.assertTemplateUsed(response, 'my_git/repositories/repositories.html')

    def test_get_public_repositories(self):
        response = self.client.get(reverse('explore'))

        self.assertEqual(response.status_code, 200)
        # repository in setUp is private
        self.assertEqual(len(response.context['repositories'].all()), 0)
        self.assertTemplateUsed(response, 'my_git/explore.html')

        # add two new public repositories
        Repository.objects.create(name="repo_new1", description="desc", owner=self.user, type="public")
        Repository.objects.create(name="repo_new2", description="desc", owner=self.user, type="public")

        response = self.client.get(reverse('explore'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['repositories'].all()), 2)
        self.assertEqual(response.context['repositories'][0].name, 'repo_new2')
        self.assertEqual(response.context['repositories'][1].name, 'repo_new1')

    def test_get_starred_repositories(self):
        response = self.client.get(reverse('stars'))

        self.assertEqual(response.status_code, 200)
        # repository in setUp is not starred
        self.assertEqual(len(response.context['repositories'].all()), 0)
        self.assertTemplateUsed(response, 'my_git/stars.html')

        # add new repository and star it
        Repository.objects.create(name="repo_new1", description="desc", owner=self.user, type="public", star=True)

        response = self.client.get(reverse('stars'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['repositories'].all()), 1)

    def test_star_repository(self):
        response = self.client.get(reverse('stars'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['repositories'].all()), 0)

        # star repository
        self.client.post(reverse('stars'), {'repo_star': "True", 'repo_id': self.repository.id})

        response = self.client.get(reverse('stars'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['repositories'].all()), 1)

    def test_get_repository(self):
        repository = Repository.objects.get(name="repo")

        response = self.client.get("/repositories/repo")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['repository'], repository)
        self.assertTemplateUsed(response, 'my_git/repositories/repository_preview.html')

    def test_create_repository_with_form(self):
        # create new repository
        response = self.client.post("/new/",
                                    {'repository_name': "repo_test", 'description': "desc_test", "type": "private"})

        # we are redirected to the repositories page
        self.assertEqual(response.status_code, 302)

        # check if the new repository is added
        repository = Repository.objects.get(name="repo_test")
        self.assertTrue(isinstance(repository, Repository))
        self.assertEqual(repository.name, "repo_test")
        self.assertEqual(repository.description, "desc_test")
        self.assertEqual(repository.type, "private")

        # open repositories page
        response = self.client.get(reverse('repositories'))
        self.assertEqual(response.status_code, 200)

        # check if the new repository is being displayed
        self.assertEqual(len(response.context['repositories'].all()), 2)

    def test_add_collaborator(self):
        # create new user
        collaborator = User.objects.create(username="collab", password="pass1", email="collab@gmail.com")

        response = self.client.post("/repositories/repo/settings",
                                    {'btn-add-collaborator': '', 'collaborator': 'collab'})

        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.repository.name, "repo")
        self.assertTrue(self.repository.collaborators.exists())
        self.assertEqual(self.repository.collaborators.all()[0].username, collaborator.username)

    def test_rename_repository(self):
        # open settings page and rename repository
        response = self.client.post("/repositories/repo/settings", {'btn-rename': "", 'value': 'repo_new'})

        self.assertEqual(response.status_code, 302)

        repository = Repository.objects.get(name="repo_new")
        self.assertNotEqual(repository, "repo")
        self.assertEqual(repository.name, "repo_new")

    def test_delete_repository(self):
        # open settings page and delete repository
        response = self.client.post("/repositories/repo/settings", {'btn-delete': ""})

        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('repositories'))
        self.assertEqual(len(response.context['repositories'].all()), 0)

    def test_insights_page(self):
        response = self.client.get('/repositories/repo/insights')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['repository'], self.repository)
        self.assertEqual(response.context['logged_user'], self.user)
        self.assertEqual(len(response.context['open_issues']), 0)
        self.assertEqual(len(response.context['closed_issues']), 0)
        self.assertTemplateUsed(response, 'my_git/repositories/insights.html')

        milestone = Milestone.objects.create(title="", due_date=datetime.now(), open=True,
                                                  repository=self.repository)
        issue = Issue.objects.create(title="Title", content="Content", date=datetime.now(), open=True,
                                          milestone=milestone, user=self.user, repository=self.repository)

        response = self.client.get('/repositories/repo/insights')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['repository'], self.repository)
        self.assertEqual(len(response.context['open_issues']), 1)
        self.assertEqual(response.context['open_issues'][0].title, 'Title')


class WikiTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="user", password="pass1", email="user@gmail.com")
        self.repository = Repository.objects.create(name="repo", description="desc", owner=self.user, type="private")
        self.wiki = Wiki.objects.create(title="Title", content="Content", repository=self.repository)

        session = self.client.session
        session['user'] = 'user'
        session.save()

    def test_get_wiki(self):
        response = self.client.get('/repositories/repo/wiki')

        self.assertEqual(response.status_code, 200)
        # at the moment there are no wiki pages
        self.assertEqual(len(response.context['pages']), 1)
        self.assertEqual(response.context['pages'][0].title, 'Title')
        self.assertEqual(response.context['pages'][0].content, 'Content')
        self.assertTemplateUsed(response, 'my_git/wiki/wiki.html')

        # add one wiki page
        self.client.post('/repositories/repo/wiki/new', {'title': 'New title', 'content': 'Content1'})

        response = self.client.get('/repositories/repo/wiki')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pages']), 2)

    def test_create_wiki_page(self):
        response = self.client.post('/repositories/repo/wiki/new', {'title': 'Test title', 'content': 'Test content'})

        self.assertEqual(response.status_code, 200)

        wiki = Wiki.objects.get(repository=self.repository, title='Test title')

        self.assertIsInstance(wiki, Wiki)
        self.assertEqual(wiki.title, "Test title")
        self.assertEqual(wiki.content, "Test content")
        self.assertEqual(wiki.repository, self.repository)

    def test_get_wiki_pages(self):
        response = self.client.get('/repositories/repo/wiki/Title')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], self.wiki)
        self.assertTemplateUsed(response, 'my_git/wiki/wiki_page_preview.html')


class IssueTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="user", password="pass1", email="user@gmail.com")
        self.repository = Repository.objects.create(name="repo", description="desc", owner=self.user, type="private")
        self.milestone = Milestone.objects.create(title="", due_date=datetime.now(), open=True,
                                                  repository=self.repository)
        self.issue = Issue.objects.create(title="Title", content="Content", date=datetime.now(), open=True,
                                          milestone=self.milestone, user=self.user, repository=self.repository)

        session = self.client.session
        session['user'] = 'user'
        session.save()

    def test_create_issues(self):
        issue = Issue.objects.get(id=self.issue.id)

        self.assertIsInstance(issue, Issue)
        self.assertEqual(issue.title, "Title")
        self.assertEqual(issue.content, "Content")
        self.assertEqual(issue.open, True)
        self.assertEqual(issue.milestone, self.milestone)
        self.assertEqual(issue.user, self.user)
        self.assertEqual(issue.repository, self.repository)

    def test_get_issues(self):
        response = self.client.get('/repositories/repo/issues')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['issues'].all()), 1)
        self.assertEqual(response.context['issues'][0].title, 'Title')
        self.assertEqual(response.context['issues'][0].content, 'Content')
        self.assertEqual(response.context['issues'][0].open, True)

        self.assertTemplateUsed(response, 'my_git/issues/issues.html')

    def test_get_issue(self):
        response = self.client.get('/repositories/repo/issues/' + str(self.issue.id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['issue'], self.issue)
        self.assertTemplateUsed(response, 'my_git/issues/issue_view.html')
