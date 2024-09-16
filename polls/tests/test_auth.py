from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from mysite import settings
from polls.models import Question, Choice


class UserAuthTest(TestCase):

    def setUp(self):
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()
        # we need a poll question to test voting
        q = Question.objects.create(question_text="First Poll Question")
        q.save()
        # a few choices
        for n in range(1, 4):
            choice = Choice(choice_text=f"Choice {n}", question=q)
            choice.save()
        self.question = q

    def test_logout(self):
        """A user can logout using the logout url.

        As an authenticated user,
        when I visit /accounts/logout/
        then I am logged out
        and then redirected to the login page.
        """
        logout_url = reverse("logout")
        self.assertTrue(
            self.client.login(username=self.username, password=self.password)
        )
        form_data = {}
        response = self.client.post(logout_url, form_data)
        self.assertEqual(302, response.status_code)

        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """A user can login using the login view."""
        login_url = reverse("login")

        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)

        form_data = {"username": "testuser",
                     "password": "FatChance!"
                     }
        response = self.client.post(login_url, form_data)

        self.assertEqual(302, response.status_code)

        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """Authentication is required to submit a vote.

        As an unauthenticated user,
        when I submit a vote for a question,
        then I am redirected to the login page
          or I receive a 403 response (FORBIDDEN)
        """
        vote_url = reverse('polls:vote', args=[self.question.id])

        choice = self.question.choice_set.first()

        form_data = {"choice": f"{choice.id}"}
        response = self.client.post(vote_url, form_data)

        self.assertEqual(response.status_code, 302)

        login_with_next = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_with_next)

    def test_invalid_login(self):
        """A user cannot login with invalid credentials."""
        login_url = reverse("login")
        form_data = {"username": "wronguser", "password": "WrongPassword!"}
        response = self.client.post(login_url, form_data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "Please enter a correct username and password.")

    def test_vote_as_authenticated_user(self):
        """An authenticated user can vote for a question."""
        self.client.login(username=self.username, password=self.password)
        vote_url = reverse('polls:vote', args=[self.question.id])
        choice = self.question.choice_set.first()

        form_data = {"choice": f"{choice.id}"}
        response = self.client.post(vote_url, form_data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('polls:results', args=[self.question.id]))

    def test_admin_access_with_admin_user(self):
        """Admin users can access the admin page."""
        admin_user = User.objects.create_superuser(
            username="adminuser",
            password="SuperSecretPassword!123",
            email="adminuser@nowhere.com"
        )
        self.client.login(username="adminuser", password="SuperSecretPassword!123")
        admin_url = reverse('admin:index')
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, 200)
