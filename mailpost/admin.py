from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Client, CustomUser, Mailing, MailingAttempt, Message


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ["email", "username", "is_verified", "is_staff"]
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("is_verified", "verification_token")}),)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Client)
admin.site.register(Message)
admin.site.register(Mailing)
admin.site.register(MailingAttempt)
