from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Client, CustomUser, Mailing, MailingAttempt, Message


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "username", "is_verified", "is_staff")
    list_filter = ("is_verified", "is_staff", "is_superuser")
    fieldsets = UserAdmin.fieldsets + (
        ("Verification", {"fields": ("is_verified", "verification_token")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Verification", {"fields": ("is_verified", "verification_token")}),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "owner")
    list_filter = ("owner",)
    search_fields = ("email", "full_name")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "owner")
    list_filter = ("owner",)
    search_fields = ("subject", "body")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("start_datetime", "status", "owner")
    list_filter = ("status", "owner")
    filter_horizontal = ("clients",)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("mailing", "attempt_datetime", "status")
    list_filter = ("status", "mailing")
    readonly_fields = ("mailing", "attempt_datetime", "status", "server_response")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
