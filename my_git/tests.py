from django.test import TestCase, RequestFactory
from my_git.models import *
from my_git.views import *
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse
from django.utils import timezone


########################################################################################################################
################################################ REPOSITORY TESTS ######################################################
########################################################################################################################

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
        Issue.objects.create(title="Title", content="Content", date=timezone.now(), open=True,
                             milestone=milestone, user=self.user, repository=self.repository)

        response = self.client.get('/repositories/repo/insights')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['repository'], self.repository)
        self.assertEqual(len(response.context['open_issues']), 1)
        self.assertEqual(response.context['open_issues'][0].title, 'Title')


########################################################################################################################
################################################## WIKI TESTS ##########################################################
########################################################################################################################

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


########################################################################################################################
################################################## ISSUE TESTS #########################################################
########################################################################################################################

class IssueTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="user", password="pass1", email="user@gmail.com")
        self.repository = Repository.objects.create(name="repo", description="desc", owner=self.user, type="private")
        self.milestone = Milestone.objects.create(title="", due_date=datetime.now(), open=True,
                                                  repository=self.repository)
        self.issue = Issue.objects.create(title="Title", content="Content", date=timezone.now(), open=True,
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


########################################################################################################################
################################################## USER TESTS ##########################################################
########################################################################################################################

class UserTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="user", password="pass1", email="user@gmail.com")

        session = self.client.session
        session['user'] = 'user'
        session.save()

    def test_login(self):
        response = self.client.post(reverse('login'), {'email': 'user@gmail.com', 'password': 'pass1'})

        self.assertEqual(response.status_code, 302)

    def test_update_user_profile(self):
        self.client.post(reverse('profile_update'), {'email': 'new_mail@gmail.com', 'password': '',
                                                     'username': 'user'})

        user = User.objects.get(username='user')

        self.assertEquals(user.username, 'user')
        self.assertEquals(user.email, 'new_mail@gmail.com')
        self.assertNotEquals(user.email, 'user@gmail.com')
        self.assertEquals(user.password, 'pass1')


########################################################################################################################
################################################## MILESTONE TESTS #####################################################
########################################################################################################################

class MilestoneTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="user", password="pass1", email="user@gmail.com")
        self.repository = Repository.objects.create(name="repo", description="desc", owner=self.user, type="private")
        self.milestone1 = Milestone.objects.create(title="Title", due_date=timezone.now(), open=True,
                                                   repository=self.repository, description="desc1")
        self.milestone2 = Milestone.objects.create(title="Title2", due_date=datetime.now(), open=False,
                                                   repository=self.repository, description="desc2")
        session = self.client.session
        session['user'] = 'user'
        session.save()

    def test_get_milestones(self):
        response = self.client.get('/repositories/repo/milestones')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['milestones'].all()), 2)
        self.assertEqual(response.context['milestones'][1].title, self.milestone1.title)
        self.assertEqual(response.context['milestones'][1].description, self.milestone1.description)
        self.assertEqual(response.context['milestones'][1].open, self.milestone1.open)
        self.assertEqual(response.context['milestones'][1].repository, self.milestone1.repository)

    def test_close_milestone(self):
        response = self.client.post('/repositories/repo/milestones',
                                    {'milestoneId': self.milestone1.id, 'closeBtn': ''})

        milestone = Milestone.objects.get(id=self.milestone1.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(milestone.open, False)

    def test_reopen_milestone(self):
        response = self.client.post('/repositories/repo/milestones',
                                    {'milestoneId': self.milestone2.id, 'reopenBtn': ''})

        milestone = Milestone.objects.get(id=self.milestone2.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(milestone.open, True)

    def test_delete_milestone(self):
        response = self.client.post('/repositories/repo/milestones',
                                    {'milestoneId': self.milestone2.id, 'deleteBtn': ''})

        self.assertEqual(response.status_code, 200)

        # get all milestones
        response = self.client.get('/repositories/repo/milestones')

        # one milestone is deleted
        self.assertEqual(len(response.context['milestones'].all()), 1)

    def test_create_milestone(self):
        response = self.client.post('/repositories/repo/milestones/new',
                                    {'titleInput': 'Title test', 'dateInput': '2019-10-10',
                                     'descriptionInput': 'Desc test'})

        milestone = Milestone.objects.get(title="Title test", description='Desc test', repository=self.repository)

        self.assertEqual(response.status_code, 302)
        self.assertIsInstance(milestone, Milestone)
        self.assertEqual(milestone.title, "Title test")
        self.assertEqual(milestone.description, "Desc test")
        self.assertEqual(milestone.open, True)
        self.assertEqual(milestone.repository, self.repository)

    def test_update_milestone(self):
        response = self.client.post('/repositories/repo/milestones/' + str(self.milestone1.id),
                                    {'titleInput': 'Title updated', 'dateInput': '2019-10-10',
                                     'descriptionInput': self.milestone1.description})

        milestone = Milestone.objects.get(id=self.milestone1.id)

        self.assertEqual(response.status_code, 302)
        self.assertIsInstance(milestone, Milestone)
        self.assertEqual(milestone.title, "Title updated")
        self.assertEqual(milestone.description, self.milestone1.description)
        self.assertEqual(milestone.open, self.milestone1.open)
        self.assertEqual(milestone.repository, self.milestone1.repository)


########################################################################################################################
################################################## LABEL TESTS #########################################################
########################################################################################################################


class LabelTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="user", password="pass1", email="user@gmail.com")
        self.repository = Repository.objects.create(name="repo", description="desc", owner=self.user, type="private")
        self.label = Label.objects.create(name="red", description="label1", color="#FFFFFF")

        session = self.client.session
        session['user'] = 'user'
        session.save()

    def test_get_labels(self):
        response = self.client.get('/repositories/repo/labels')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['labels'].all()), 1)
        self.assertEqual(response.context['labels'][0].name, self.label.name)
        self.assertEqual(response.context['labels'][0].description, self.label.description)
        self.assertEqual(response.context['labels'][0].color, self.label.color)

    def test_update_label(self):
        response = self.client.post('/repositories/repo/labels', {'labelId': self.label.id, 'updateBtn': '',
                                                                  'editName': self.label.name,
                                                                  'editDescription': 'New desc',
                                                                  'editColor': self.label.color})
        self.assertEqual(response.status_code, 200)

        label = Label.objects.get(id=self.label.id)

        self.assertIsInstance(label, Label)
        self.assertEqual(label.name, self.label.name)
        self.assertEqual(label.description, "New desc")
        self.assertEqual(label.color, self.label.color)

    def test_create_new_label(self):
        response = self.client.post('/repositories/repo/labels/new', {'nameInput': "Test label name",
                                                                      'descriptionInput': 'Test label desc',
                                                                      'color': "#000000"})
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/repositories/repo/labels')
        self.assertEqual(len(response.context['labels'].all()), 2)
        self.assertEqual(response.context['labels'][1].name, "Test label name")
        self.assertEqual(response.context['labels'][1].description, "Test label desc")
        self.assertEqual(response.context['labels'][1].color, "#000000")


########################################################################################################################
################################################## COMMIT TESTS ########################################################
########################################################################################################################


class CommitTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="user", password="pass1", email="user@gmail.com")
        self.repository = Repository.objects.create(name="repo", description="desc", owner=self.user, type="private")

        session = self.client.session
        session['user'] = 'user'
        session.save()

    def test_create_commit(self):
        response = self.client.post('/repositories/repo/commits/new', {'messageInput': 'Test commit'})

        self.assertEqual(response.status_code, 302)

        response = self.client.get('/repositories/repo')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context['commits'].all()), 1)
        self.assertEqual(response.context['commits'][0].message, 'Test commit')
        self.assertEqual(response.context['commits'][0].user, self.user)
        self.assertEqual(response.context['commits'][0].repository, self.repository)


########################################################################################################################
################################################## BRANCH TESTS ########################################################
########################################################################################################################

class BranchTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="user", password="pass1", email="user@gmail.com")
        self.repository = Repository.objects.create(name="repo", description="desc", owner=self.user,
                                                    type="private")
        self.branch = Branch.objects.create(user=self.user, repository=self.repository, name="branch1")

        session = self.client.session
        session['user'] = 'user'
        session.save()

    def test_get_branches(self):
        response = self.client.get('/repositories/repo/branches')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['branches']), 2)
        self.assertEqual(response.context['branches'][0].name, 'master')
        self.assertEqual(response.context['branches'][0].user, self.branch.user)

        # branch from the setUp
        self.assertEqual(response.context['branches'][1].name, self.branch.name)
        self.assertEqual(response.context['branches'][1].user, self.branch.user)
        self.assertEqual(response.context['branches'][1].repository, self.repository)

    def test_create_branch(self):
        response = self.client.post('/repositories/repo/branches/new', {'branchInput': 'Test branch'})

        self.assertEqual(response.status_code, 302)

        response = self.client.get('/repositories/repo/branches')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['branches']), 3)
        self.assertIsInstance(response.context['branches'][2], Branch)
        self.assertEqual(response.context['branches'][2].name, "Test branch")
        self.assertEqual(response.context['branches'][2].user, self.branch.user)
        self.assertEqual(response.context['branches'][2].repository, self.repository)
