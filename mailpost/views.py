# mailpost/views.py
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    ClientForm,
    CustomUserCreationForm,
    EmailVerificationForm,
    MailingForm,
    MessageForm,
)
from .models import Client, Mailing, Message

logger = logging.getLogger(__name__)


def home(request):
    return render(request, "home.html")


User = get_user_model()


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
                    messages.success(request, "Please check your email to verify your account.")
                else:
                    logger.warning(f"Failed to send verification email to {user.email}")
                    messages.warning(
                        request,
                        "Account created, but we couldn't send a verification email. Please contact support.",
                    )

                return redirect("login")
            except Exception as e:
                logger.error(f"Error during registration: {str(e)}", exc_info=True)
                messages.error(request, "An error occurred during registration. Please try again.")
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
                messages.success(request, "Your email has been verified. You can now log in.")
                return redirect("login")
            except User.DoesNotExist:
                form.add_error(None, "Invalid or expired verification token")
    else:
        form = EmailVerificationForm()
    return render(request, "registration/verify_email.html", {"form": form})


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
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


logger = logging.getLogger(__name__)


def send_verification_email(user):
    logger.info(f"Sending verification email to {user.email}")
    subject = "Verify your email"
    message = f"Your verification token is: {user.verification_token}"
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
    subject = "Test email from Django"
    message = "This is a test email sent from your Django application."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ["demondzr@yandex.ru"]  # Замените на ваш email для тестирования

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
def mailing_list(request):
    mailings = Mailing.objects.filter(owner=request.user)
    return render(request, "mailing_list.html", {"mailings": mailings})


@login_required
def mailing_create(request):
    if request.method == "POST":
        form = MailingForm(request.POST)
        if form.is_valid():
            mailing = form.save(commit=False)
            mailing.owner = request.user
            mailing.save()
            form.save_m2m()  # Сохраняем связи many-to-many
            return redirect("mailing_list")
    else:
        form = MailingForm()
    return render(request, "mailing_form.html", {"form": form})


@login_required
def mailing_detail(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
    return render(request, "mailing_detail.html", {"mailing": mailing})


@login_required
def mailing_update(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
    if request.method == "POST":
        form = MailingForm(request.POST, instance=mailing)
        if form.is_valid():
            form.save()
            return redirect("mailing_list")
    else:
        form = MailingForm(instance=mailing)
    return render(request, "mailing_form.html", {"form": form})


@login_required
def mailing_delete(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
    if request.method == "POST":
        mailing.delete()
        return redirect("mailing_list")
    return render(request, "mailing_confirm_delete.html", {"mailing": mailing})


# def logout_view(request):
#     logout(request)
#     return redirect("home")  # или куда вы хотите перенаправить после выхода
