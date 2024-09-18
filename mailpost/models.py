import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def generate_verification_token():
    return str(uuid.uuid4())


class Client(models.Model):
    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True, null=True)


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()


class Mailing(models.Model):
    STATUS_CHOICES = [
        ("created", "Created"),
        ("started", "Started"),
        ("completed", "Completed"),
    ]
    start_datetime = models.DateTimeField()
    periodicity = models.CharField(
        max_length=50,
        choices=[("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly")],
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Client)


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Не успешно"),
    ]

    mailing = models.ForeignKey("Mailing", on_delete=models.CASCADE)
    attempt_datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    server_response = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Попытка рассылки {self.mailing.id} - {self.status} - {self.attempt_datetime}"


class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(
        max_length=100, blank=True, default=generate_verification_token
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
