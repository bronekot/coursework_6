from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("clients/", views.ClientListView.as_view(), name="client_list"),
    path("clients/create/", views.ClientCreateView.as_view(), name="client_create"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("mailings/", views.MailingListView.as_view(), name="mailing_list"),
    path("mailings/", views.MailingListView.as_view(), name="mailing_list"),
    path("mailings/<int:pk>/", views.MailingDetailView.as_view(), name="mailing_detail"),
    path("mailings/<int:pk>/close/", views.MailingCloseView.as_view(), name="mailing_close"),
    path("mailings/<int:pk>/delete/", views.MailingDeleteView.as_view(), name="mailing_delete"),
    path("mailings/<int:pk>/update/", views.MailingUpdateView.as_view(), name="mailing_update"),
    path("mailings/create/", views.MailingCreateView.as_view(), name="mailing_create"),
    path("mailings/create/", views.MailingCreateView.as_view(), name="mailing_create"),
    path("manager/mailings/", views.manager_mailing_list, name="manager_mailing_list"),
    path(
        "manager/mailings/<int:pk>/toggle/",
        views.ManagerToggleMailingView.as_view(),
        name="manager_toggle_mailing",
    ),
    path(
        "manager/toggle-mailing/<int:mailing_id>/",
        views.manager_toggle_mailing,
        name="manager_toggle_mailing",
    ),
    # path(
    #     "manager/toggle-user/<int:user_id>/", views.manager_toggle_user, name="manager_toggle_user"
    # ),
    path("manager/users/", views.ManagerUserListView.as_view(), name="manager_user_list"),
    path(
        "manager/users/<int:pk>/toggle/",
        views.ManagerToggleUserView.as_view(),
        name="manager_toggle_user",
    ),
    path("messages/", views.MessageListView.as_view(), name="message_list"),
    path("messages/create/", views.MessageCreateView.as_view(), name="message_create"),
    path("register/", views.register, name="register"),
    path("resend-verification/", views.resend_verification, name="resend_verification"),
    path("send-test-email/", views.send_test_email, name="send_test_email"),
    path("verify-email/", views.verify_email, name="verify_email"),
]
