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
from django.db.models import Q
from .models import Choice, Question, Vote
import logging

logger = logging.getLogger(__name__)


class IndexView(generic.ListView):
    """
    A view that displays the published questions on the index page.
    """
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now())\
            .order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poll_status'] = {
            question.id: 'Open' if question.can_vote() else 'Closed' for
            question in context['latest_question_list']}
        return context


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
        Return the published questions, optionally filtered by a search query.
        """
        query = self.request.GET.get('q')

        queryset = Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")

        if query:
            queryset = queryset.filter(Q(question_text__icontains=query))

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add additional context data (poll status and the search query).
        """
        context = super().get_context_data(**kwargs)

        context['poll_status'] = 'Open' if self.object.can_vote() else 'Closed'

        context['query'] = self.request.GET.get('q', '')

        return context


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
    user = request.user
    logger.info(f"User {user.username} is voting on "
                f"question {question_id}")
    question = get_object_or_404(Question, pk=question_id)
    ip = get_client_ip(request)

    if not question.can_vote():
        logger.warning(
            f"User {user.username} tried to vote on closed question "
            f"{question_id} from {ip}")
        messages.error(request, "Voting is not allowed for this poll.")
        return redirect('polls:index')

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
        logger.info(
            f"User {user.username} selected choice {selected_choice.id} "
            f"from {ip}")

    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )

    try:
        existing_vote = Vote.objects.get(user=user, choice__question=question)
        logger.info(
            f"User {user.username} is updating their vote to choice "
            f"{selected_choice.id} on question {question_id} from {ip}")
        existing_vote.choice = selected_choice
        existing_vote.save()

    except Vote.DoesNotExist:
        logger.info(
            f"User {user.username} is voting for choice {selected_choice.id} "
            f"on question {question_id} from {ip}")
        Vote.objects.create(user=user, choice=selected_choice)

    messages.success(request,
                     f"Your vote for '{selected_choice.choice_text}' "
                     f"has been recorded.")

    return HttpResponseRedirect(reverse("polls:results",
                                        args=(question.id,)))


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
    Get a visitor's IP Address
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
        f"Failed login for {credentials.get('username', 'unknown')} "
        f"from {ip_addr}")
