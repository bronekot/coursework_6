from django.core.management.base import BaseCommand
from mailpost.tasks import send_mailing


class Command(BaseCommand):
    help = "Send mailings"

    def handle(self, *args, **kwargs):
        send_mailing()
