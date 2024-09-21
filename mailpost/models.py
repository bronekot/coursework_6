import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


def generate_verification_token():
    return uuid.uuid4().hex[:8]


class Client(models.Model):
    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="clients"
    )


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages"
    )


class Mailing(models.Model):
    STATUS_CHOICES = [
        ("created", "Создано"),
        ("started", "Запущено"),
        ("completed", "Выполнено"),
        ("closed", "Закрыто"),
    ]
    start_datetime = models.DateTimeField()
    periodicity = models.CharField(
        max_length=50,
        choices=[
            ("every_5_minutes", "Каждые 5 минут"),
            ("daily", "Ежедневно"),
            ("weekly", "Еженедельно"),
            ("monthly", "Ежемесячно"),
        ],
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Client)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mailings"
    )


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
