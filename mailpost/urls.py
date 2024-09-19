from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("clients/", views.client_list, name="client_list"),
    path("clients/create/", views.client_create, name="client_create"),
    path("messages/", views.message_list, name="message_list"),
    path("messages/create/", views.message_create, name="message_create"),
    path("mailings/", views.mailing_list, name="mailing_list"),
    path("mailings/create/", views.mailing_create, name="mailing_create"),
    path("mailings/<int:pk>/", views.mailing_detail, name="mailing_detail"),
    path("mailings/<int:pk>/update/", views.mailing_update, name="mailing_update"),
    path("mailings/<int:pk>/delete/", views.mailing_delete, name="mailing_delete"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("verify-email/", views.verify_email, name="verify_email"),
    path("send-test-email/", views.send_test_email, name="send_test_email"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("resend-verification/", views.resend_verification, name="resend_verification"),
    path("manager/mailings/", views.manager_mailing_list, name="manager_mailing_list"),
    path("manager/users/", views.manager_user_list, name="manager_user_list"),
    path(
        "manager/toggle-user/<int:user_id>/", views.manager_toggle_user, name="manager_toggle_user"
    ),
    path(
        "manager/toggle-mailing/<int:mailing_id>/",
        views.manager_toggle_mailing,
        name="manager_toggle_mailing",
    ),
    path("logout/", views.logout_view, name="logout"),
]
