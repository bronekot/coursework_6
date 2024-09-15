from django.apps import AppConfig
from time import sleep


class MailingAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mailpost"

    def ready(self):
        from .scheduler import start

        sleep(2)
        start()
