# entreprises/apps.py
from django.apps import AppConfig

class EntreprisesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'entreprises'
    verbose_name = "Entreprises"

    def ready(self):
        from . import signals 