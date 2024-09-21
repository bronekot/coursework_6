# tasks.py
import logging
from datetime import datetime

import pytz
from django.conf import settings
from django.core.mail import send_mail

from .models import Mailing, MailingAttempt

logger = logging.getLogger(__name__)


def send_mailing():
    zone = pytz.timezone(settings.TIME_ZONE)
    current_datetime = datetime.now(zone)
    mailings = Mailing.objects.filter(start_datetime__lte=current_datetime).filter(
        status__in=["created", "started"]
    )

    for mailing in mailings:
        last_attempt = (
            MailingAttempt.objects.filter(mailing=mailing).order_by("-attempt_datetime").first()
        )
        if last_attempt:
            time_diff = current_datetime - last_attempt.attempt_datetime
            if mailing.periodicity == "every_5_minutes" and time_diff.total_seconds() < 300:
                continue
            if mailing.periodicity == "daily" and time_diff.days < 1:
                continue
            elif mailing.periodicity == "weekly" and time_diff.days < 7:
                continue
            elif mailing.periodicity == "monthly" and time_diff.days < 30:
                continue

        try:
            server_response = send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[client.email for client in mailing.clients.all()],
                fail_silently=False,
            )
            logger.info(f"Email sent successfully. Server response: {server_response}")
            MailingAttempt.objects.create(
                mailing=mailing, status="success", server_response=server_response
            )
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            MailingAttempt.objects.create(mailing=mailing, status="failed", server_response=str(e))
