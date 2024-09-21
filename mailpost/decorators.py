from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def verified_email_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_verified:
                return view_func(request, *args, **kwargs)
            else:
                messages.warning(
                    request,
                    "Для выполнения этого действия необходимо подтвердить email. "
                    "Пожалуйста, проверьте свою почту и подтвердите email.",
                )
                return redirect("home")  # или другая подходящая страница
        return redirect("login")

    return _wrapped_view
    return _wrapped_view
