# mailpost/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Client, Message, Mailing
from .forms import ClientForm, MessageForm, MailingForm


def client_list(request):
    clients = Client.objects.all()
    return render(request, "client_list.html", {"clients": clients})


def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("client_list")
    else:
        form = ClientForm()
    return render(request, "client_form.html", {"form": form})


def message_list(request):
    messages = Message.objects.all()
    return render(request, "message_list.html", {"messages": messages})


def message_create(request):
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("message_list")
    else:
        form = MessageForm()
    return render(request, "message_form.html", {"form": form})


def mailing_list(request):
    mailings = Mailing.objects.all()
    return render(request, "mailing_list.html", {"mailings": mailings})


def mailing_create(request):
    if request.method == "POST":
        form = MailingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("mailing_list")
    else:
        form = MailingForm()
    return render(request, "mailing_form.html", {"form": form})
