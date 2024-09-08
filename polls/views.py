from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in, user_logged_out, \
    user_login_failed
from django.dispatch import receiver
from .models import Choice, Question
import logging

logger = logging.getLogger(__name__)


class IndexView(generic.ListView):
    """
    A view that displays the last five published questions on the index page.
    """
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    """
    A view that displays the details of a specific question.
    """
    model = Question
    template_name = "polls/detail.html"

    def get(self, request, *args, **kwargs):
        """
        Override the get method to check if voting is allowed.
        If not, redirect to the index page with an error message.
        """
        question = self.get_object()

        if not question.can_vote():
            messages.error(request, "Voting is not allowed for this question.")
            return HttpResponseRedirect(reverse("polls:index"))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now(),
                                       pk__in=[q.pk for q in Question.objects.all() if q.is_published()])


class ResultsView(generic.DetailView):
    """
    A view that displays the results of a specific question.
    """
    model = Question
    template_name = "polls/results.html"


@login_required
def vote(request, question_id):
    """
    Handle voting for a specific choice in a question.
    """
    question = get_object_or_404(Question, pk=question_id)

    if not question.can_vote():
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "Voting is not allowed for this question.",
            },
        )

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def signup(request):
    """
    Register a new user
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_passwd = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_passwd)
            login(request, user)
            return redirect('polls:index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def get_client_ip(request):
    """

    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def login_success(sender, request, user, **kwargs):
    ip_addr = get_client_ip(request)
    logger.info(f"{user.username} logged in from {ip_addr}")


@receiver(user_logged_out)
def logout_success(sender, request, user, **kwargs):
    ip_addr = get_client_ip(request)
    logger.info(f"{user.username} logged out from {ip_addr}")


@receiver(user_login_failed)
def login_fail(sender, credentials, request, **kwargs):
    ip_addr = get_client_ip(request)
    logger.warning(
        f"Failed login for {credentials.get('username', 'unknown')} from {ip_addr}")
