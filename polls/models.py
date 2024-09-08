import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


def get_time_current():
    """Return the current local time"""
    return timezone.now()


class Question(models.Model):
    """
    Create a question
    use question_text for a question and pub_date for a publishing date
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published", default=get_time_current)
    end_date = models.DateTimeField("end date for voting", null=True, blank=True)

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        """Return True if the question was published lately"""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """Return True if the current local time is >= the publication date"""
        now = timezone.now()
        return now >= self.pub_date

    def can_vote(self):
        """Return True if voting is allowed for this question"""
        now = timezone.now()
        if self.end_date is None:
            return now >= self.pub_date
        return self.pub_date <= now < self.end_date


class Choice(models.Model):
    """
    Create a choice of a specific question
    use choice_text for a choice text and votes for setting s default vote value
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    @property
    def vote(self):
        """Return the votes for this choice"""
        return Vote.objects.filter(choice=self).count()

    def __str__(self):
        return self.choice_text


class Vote(models.Model):
    """
    Create a voting information,
    contained a choice that voted and a user who made that choice
    """
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} voted for {self.choice.choice_text}"
