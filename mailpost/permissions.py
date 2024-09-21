import logging

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


class VerifiedEmailRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_verified

    def handle_no_permission(self):
        messages.warning(
            self.request,
            "Для выполнения этого действия необходимо подтвердить email. "
            "Пожалуйста, проверьте свою почту и подтвердите email.",
        )
        return redirect("home")


class IsOwnerOrManagerMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        is_owner = self.request.user == obj.owner
        is_manager = self.request.user.groups.filter(name="Managers").exists()
        logger.debug(f"User: {self.request.user}, Is owner: {is_owner}, Is manager: {is_manager}")
        return is_owner or is_manager


class IsManagerMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name="Managers").exists()
