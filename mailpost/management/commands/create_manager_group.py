from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from mailpost.models import Client, CustomUser, Mailing, Message


class Command(BaseCommand):
    help = "Creates manager group with specific permissions"

    def handle(self, *args, **options):
        manager_group, created = Group.objects.get_or_create(name="Managers")

        if created:
            # Permissions for Mailing
            mailing_content_type = ContentType.objects.get_for_model(Mailing)
            view_mailing = Permission.objects.get(
                content_type=mailing_content_type, codename="view_mailing"
            )
            manager_group.permissions.add(view_mailing)

            # Permissions for Client
            client_content_type = ContentType.objects.get_for_model(Client)
            view_client = Permission.objects.get(
                content_type=client_content_type, codename="view_client"
            )
            manager_group.permissions.add(view_client)

            # Permissions for Message
            message_content_type = ContentType.objects.get_for_model(Message)
            view_message = Permission.objects.get(
                content_type=message_content_type, codename="view_message"
            )
            manager_group.permissions.add(view_message)

            # Permissions for CustomUser
            user_content_type = ContentType.objects.get_for_model(CustomUser)
            view_user = Permission.objects.get(
                content_type=user_content_type, codename="view_customuser"
            )
            change_user = Permission.objects.get(
                content_type=user_content_type, codename="change_customuser"
            )
            manager_group.permissions.add(view_user, change_user)

            self.stdout.write(self.style.SUCCESS("Successfully created manager group"))
        else:
            self.stdout.write(self.style.WARNING("Manager group already exists"))
