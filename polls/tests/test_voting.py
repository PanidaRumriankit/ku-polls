import datetime

from django.test import TestCase
from django.utils import timezone
from polls.models import Question


class QuestionVoteTests(TestCase):
    def test_can_vote_with_future_end_date(self):
        """
        can_vote() returns True if the current date and time is between
        pub_date and end_date.
        """
        pub_time = timezone.now() - datetime.timedelta(days=2)
        end_time = timezone.now() + datetime.timedelta(days=2)
        question = Question(pub_date=pub_time, end_date=end_time)
        self.assertTrue(question.can_vote())

    def test_can_vote_with_past_end_date(self):
        """
        can_vote() returns False if the current date and time is after
        the end_date.
        """
        pub_time = timezone.now() - datetime.timedelta(days=3)
        end_time = timezone.now() - datetime.timedelta(days=1)
        question = Question(pub_date=pub_time, end_date=end_time)
        self.assertFalse(question.can_vote())

    def test_can_vote_with_now_end_date(self):
        """
        can_vote() returns False if current date time is end_date
        """
        pub_time = timezone.now() - datetime.timedelta(days=1)
        question = Question(pub_date=pub_time, end_date=timezone.now())
        self.assertFalse(question.can_vote())

    def test_can_vote_with_no_end_date(self):
        """
        can_vote() returns True if there is no end_date and the current
        date and time is after pub_date.
        """
        pub_time = timezone.now() - datetime.timedelta(days=1)
        question = Question(pub_date=pub_time, end_date=None)
        self.assertTrue(question.can_vote())
