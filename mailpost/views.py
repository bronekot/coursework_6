import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
    View,
)

from .decorators import verified_email_required
from .forms import (
    ClientForm,
    CustomUserCreationForm,
    EmailVerificationForm,
    MailingForm,
    MessageForm,
)
from .models import Client, Mailing, Message
from .permissions import (
    IsManagerMixin,
    IsOwnerOrManagerMixin,
    VerifiedEmailRequiredMixin,
)

User = get_user_model()


def home(request):
    return render(request, "home.html")


logger = logging.getLogger(__name__)


def register(request):
    logger.info("Register view called")
    if request.method == "POST":
        logger.info("POST request received")
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            logger.info("Form is valid")
            try:
                user = form.save(commit=False)
                user.is_active = True
                user.save()
                logger.info(f"User created: {user.email}")

                logger.info(f"Attempting to send verification email to {user.email}")
                if send_verification_email(user):
                    logger.info(f"Verification email sent successfully to {user.email}")
                    messages.success(
                        request,
                        "Пожалуйста, проверьте электронную почту, чтобы подтвердить аккаунт.",
                    )
                else:
                    logger.warning(f"Failed to send verification email to {user.email}")
                    messages.warning(
                        request,
                        "Аккаунт создан, но мы не смогли отправить письмо с подтверждением.",
                        "Пожалуйста, не связывайтесь с поддержкой.",
                    )

                return redirect("login")
            except Exception as e:
                logger.error(f"Error during registration: {str(e)}", exc_info=True)
                messages.error(
                    request, "Во время регистрации произошла ошибка. Пожалуйста, попробуйте снова."
                )
        else:
            logger.warning("Form is invalid")
            logger.warning(f"Form errors: {form.errors}")
    else:
        logger.info("GET request received")
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})


def verify_email(request):
    if request.method == "POST":
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data["verification_token"]
            try:
                user = User.objects.get(verification_token=token, is_verified=False)
                user.is_verified = True
                user.verification_token = ""
                user.save()
                messages.success(
                    request, "Ваш email подтвержден. Теперь вы можете авторизоваться."
                )
                return redirect("login")
            except User.DoesNotExist:
                form.add_error(None, "Неверный или просроченный токен подтверждения")
    else:
        form = EmailVerificationForm()
    return render(request, "registration/verify_email.html", {"form": form})


@never_cache
@vary_on_cookie
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Неверное имя пользователя или пароль.")
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


logger = logging.getLogger(__name__)


def send_verification_email(user):
    logger.info(f"Sending verification email to {user.email}")
    subject = "Подтвердите свой email"
    message = f"Ваш токен подтверждения: {user.verification_token}"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    try:
        result = send_mail(subject, message, from_email, recipient_list)
        logger.info(f"send_mail result: {result}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}", exc_info=True)
        logger.error(f"Email details: subject={subject}, from={from_email}, to={recipient_list}")
        return False


def send_test_email(request):
    subject = "Тестовое письмо из Django"
    message = "Это тестовое письмо, отправленное из приложения Django."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ["test@example.com"]  # Замените на ваш email для тестирования

    try:
        send_mail(subject, message, from_email, recipient_list)
        return HttpResponse("Test email sent successfully!")
    except Exception as e:
        return HttpResponse(f"Failed to send test email. Error: {str(e)}")


@login_required
def client_list(request):
    clients = Client.objects.filter(owner=request.user)
    return render(request, "client_list.html", {"clients": clients})


@login_required
@verified_email_required
def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.owner = request.user
            client.save()
            return redirect("client_list")
    else:
        form = ClientForm()
    return render(request, "client_form.html", {"form": form})


@login_required
def message_list(request):
    messages = Message.objects.filter(owner=request.user)
    return render(request, "message_list.html", {"messages": messages})


@login_required
@verified_email_required
def message_create(request):
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.owner = request.user
            message.save()
            return redirect("message_list")
    else:
        form = MessageForm()
    return render(request, "message_form.html", {"form": form})


@login_required
def resend_verification(request):
    if not request.user.is_verified:
        if send_verification_email(request.user):
            messages.success(
                request, "Письмо с подтверждением отправлено. Пожалуйста, проверьте вашу почту."
            )
        else:
            messages.error(
                request,
                "Не удалось отправить письмо с подтверждением. Пожалуйста, попробуйте позже.",
            )
    else:
        messages.info(request, "Ваш email уже подтвержден.")
    return redirect("home")


def is_manager(user):
    return user.groups.filter(name="Managers").exists()


@user_passes_test(is_manager)
def manager_mailing_list(request):
    mailings = Mailing.objects.all()
    return render(request, "manager/mailing_list.html", {"mailings": mailings})


@user_passes_test(is_manager)
def manager_user_list(request):
    users = User.objects.all()
    return render(request, "manager/user_list.html", {"users": users})


# @user_passes_test(is_manager)
# def manager_toggle_user(request, user_id):
#     user = get_object_or_404(User, id=user_id)
#     user.is_active = not user.is_active
#     user.save()
#     action = "activated" if user.is_active else "deactivated"
#     messages.success(request, f"User {user.username} has been {action}.")
#     return redirect("manager_user_list")


@user_passes_test(is_manager)
def manager_toggle_mailing(request, mailing_id):
    mailing = get_object_or_404(Mailing, id=mailing_id)
    mailing.status = "completed" if mailing.status != "completed" else "created"
    mailing.save()
    messages.success(request, f"Mailing status has been changed to {mailing.status}.")
    return redirect("manager_mailing_list")


@never_cache
@require_http_methods(["GET", "POST"])
def logout_view(request):
    auth_logout(request)
    return redirect("home")


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        if self.request.user.groups.filter(name="Managers").exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Mailing
    template_name = "mailing_detail.html"

    def test_func(self):
        mailing = self.get_object()
        user = self.request.user
        return (
            user.is_authenticated
            and user.is_verified
            and (user == mailing.owner or user.groups.filter(name="Managers").exists())
        )

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("У вас нет разрешения на просмотр этой рассылки")
        return super().handle_no_permission()


class MailingCreateView(LoginRequiredMixin, VerifiedEmailRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing_form.html"
    success_url = reverse_lazy("mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingCloseView(LoginRequiredMixin, RedirectView):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
        mailing.status = "closed"
        mailing.save()
        messages.success(request, "Рассылка закрыта успешно.")
        return redirect("mailing_list")


class MailingUpdateView(LoginRequiredMixin, IsOwnerOrManagerMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing_form.html"
    success_url = reverse_lazy("mailing_list")


class MailingDeleteView(LoginRequiredMixin, IsOwnerOrManagerMixin, DeleteView):
    model = Mailing
    template_name = "mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing_list")


class ManagerUserListView(IsManagerMixin, ListView):
    model = User
    template_name = "manager/user_list.html"
    context_object_name = "users"


class ManagerToggleUserView(IsManagerMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        action = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User {user.username} has been {action}.")
        return redirect("manager_user_list")


class ManagerToggleMailingView(IsManagerMixin, UpdateView):
    model = Mailing
    fields = ["status"]
    template_name = "manager/toggle_mailing.html"
    success_url = reverse_lazy("mailing_list")

    def form_valid(self, form):
        mailing = form.save()
        messages.success(self.request, f"Mailing status has been changed to {mailing.status}.")
        return super().form_valid(form)

    success_url = reverse_lazy("mailing_list")


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, VerifiedEmailRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "client_form.html"
    success_url = reverse_lazy("client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, VerifiedEmailRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "message_form.html"
    success_url = reverse_lazy("message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
