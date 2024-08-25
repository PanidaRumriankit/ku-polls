import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    """
    Create a question
    use question_text for a question and pub_date for a publishing date
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    """
    Create a choice of a specific question
    use choice_text for a choice text and votes for setting s default vote value
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
