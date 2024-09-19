from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Client, Mailing, Message

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class EmailVerificationForm(forms.Form):
    verification_token = forms.CharField(max_length=100)


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ["owner"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        exclude = ["owner"]


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        exclude = ["owner"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(MailingForm, self).__init__(*args, **kwargs)
        if user:
            self.fields["clients"].queryset = Client.objects.filter(owner=user)
            self.fields["message"].queryset = Message.objects.filter(owner=user)
