from django.apps import AppConfig


class PollsConfig(AppConfig):
    """Configures the Polls application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'
