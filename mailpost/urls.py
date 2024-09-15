from django.urls import path
from .views import (
    client_list,
    client_create,
    message_list,
    message_create,
    mailing_list,
    mailing_create,
)

urlpatterns = [
    path("clients/", client_list, name="client_list"),
    path("clients/create/", client_create, name="client_create"),
    path("messages/", message_list, name="message_list"),
    path("messages/create/", message_create, name="message_create"),
    path("mailings/", mailing_list, name="mailing_list"),
    path("mailings/create/", mailing_create, name="mailing_create"),
]
