from django.test import TestCase, RequestFactory
from my_git.models import *

#
class RepositoryTests(TestCase):
    class TestSimpleApp:
        def test_one(self):
            x = "my simple app test"
            assert 'simple app' in x

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="user", password="pass1", email="user@gmail.com")
        self.repository = Repository.objects.create(name="repo1", description="desc1", owner=self.user, type="private")

    def test_create_repository(self):
        # self.assertTrue(isinstance(self.repository, Repository))
        self.assertEqual(self.repository.name, "repo")
        # self.assertEqual(self.repository.description, "desc1")
        # self.assertEqual(self.repository.owner, self.user)
        # self.assertEqual(self.repository.type, "private")

#     def test_repository_view(self):
#         request = self.factory.get('/repositories/' + self.repository.name)
#         self.assertEqual(response.status_code, 200)
