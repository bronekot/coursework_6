from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from mailpost.models import Client as MailClient
from mailpost.models import Mailing, MailingAttempt, Message

from .forms import ClientForm, MailingForm, MessageForm

User = get_user_model()


def print_debug_info(test_case, response):
    print(f"\nDebug info for {test_case.__class__.__name__}.{test_case._testMethodName}")
    print(f"Status code: {response.status_code}")
    print(f"Response content: {response.content.decode('utf-8')[:500]}")
    print(f"Current user: {test_case.client.session.get('_auth_user_id')}")
    if hasattr(test_case, "manager"):
        print(f"Manager permissions: {test_case.manager.get_all_permissions()}")
    print("---")


User = get_user_model()


class MailingPermissionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="password123"
        )
        self.user1.is_verified = True
        self.user1.save()

        managers_group, _ = Group.objects.get_or_create(name="Managers")
        self.user1.groups.add(managers_group)

        self.message = Message.objects.create(
            subject="Test Subject", body="Test Body", owner=self.user1
        )
        self.mailing = Mailing.objects.create(
            start_datetime=timezone.now(),
            periodicity="daily",
            status="created",
            message=self.message,
            owner=self.user1,
        )

    def test_owner_can_access_own_mailing(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse("mailing_detail", args=[self.mailing.id]))
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_access_others_mailing(self):
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="otherpass123"
        )
        other_user.is_verified = True
        other_user.save()

        self.client.force_login(other_user)
        response = self.client.get(reverse("mailing_detail", args=[self.mailing.id]))
        self.assertEqual(response.status_code, 403)


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client = MailClient.objects.create(
            email="client@example.com",
            full_name="Test Client",
            comment="Test comment",
            owner=self.user,
        )
        self.message = Message.objects.create(
            subject="Test Subject", body="Test Body", owner=self.user
        )
        self.mailing = Mailing.objects.create(
            start_datetime=timezone.now(),
            periodicity="daily",
            status="created",
            message=self.message,
            owner=self.user,
        )
        self.mailing.clients.add(self.client)

    def test_client_creation(self):
        self.assertEqual(self.client.email, "client@example.com")
        self.assertEqual(self.client.full_name, "Test Client")
        self.assertEqual(self.client.owner, self.user)

    def test_message_creation(self):
        self.assertEqual(self.message.subject, "Test Subject")
        self.assertEqual(self.message.body, "Test Body")
        self.assertEqual(self.message.owner, self.user)

    def test_mailing_creation(self):
        self.assertEqual(self.mailing.periodicity, "daily")
        self.assertEqual(self.mailing.status, "created")
        self.assertEqual(self.mailing.message, self.message)
        self.assertEqual(self.mailing.owner, self.user)
        self.assertIn(self.client, self.mailing.clients.all())


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.user.is_verified = True
        self.user.save()
        self.client.login(email="test@example.com", password="testpass123")

        # Add necessary permissions
        content_type = ContentType.objects.get_for_model(Mailing)
        view_mailing_permission = Permission.objects.get(
            content_type=content_type, codename="view_mailing"
        )
        self.user.user_permissions.add(view_mailing_permission)

        # Create a mailing owned by this user
        self.mailing = Mailing.objects.create(
            start_datetime=timezone.now(),
            periodicity="daily",
            status="created",
            message=Message.objects.create(subject="Test", body="Test", owner=self.user),
            owner=self.user,
        )

    def test_mailing_detail_view(self):
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(reverse("mailing_detail", args=[self.mailing.id]))
        # print_debug_info(self, response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "mailing_detail.html")

    def test_client_list_view(self):
        response = self.client.get(reverse("client_list"))
        # print_debug_info(self, response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client_list.html")

    def test_client_create_view(self):
        self.user.is_verified = True
        self.user.save()
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.post(
            reverse("client_create"),
            {
                "email": "newclient@example.com",
                "full_name": "New Client",
                "comment": "New comment",
            },
        )
        # print_debug_info(self, response)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(MailClient.objects.filter(email="newclient@example.com").exists())

    def test_mailing_list_view(self):
        response = self.client.get(reverse("mailing_list"))
        # print_debug_info(self, response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "mailing_list.html")

    def test_unverified_user_cannot_create_client(self):
        self.user.is_verified = False
        self.user.save()
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.post(
            reverse("client_create"),
            {
                "email": "newclient@example.com",
                "full_name": "New Client",
                "comment": "New comment",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect to home page
        self.assertFalse(MailClient.objects.filter(email="newclient@example.com").exists())

    def test_user_cannot_access_others_mailings(self):
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="otherpass123"
        )
        other_user.is_verified = True
        other_user.save()

        other_message = Message.objects.create(subject="Test", body="Test", owner=other_user)
        other_mailing = Mailing.objects.create(
            start_datetime=timezone.now(),
            periodicity="daily",
            status="created",
            message=other_message,
            owner=other_user,
        )

        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(reverse("mailing_detail", args=[other_mailing.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden


class FormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_client_form_valid(self):
        form_data = {
            "email": "client@example.com",
            "full_name": "Test Client",
            "comment": "Test comment",
        }
        form = ClientForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_client_form_invalid(self):
        form_data = {"email": "invalid-email", "full_name": "", "comment": "Test comment"}
        form = ClientForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_message_form_valid(self):
        form_data = {"subject": "Test Subject", "body": "Test Body"}
        form = MessageForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_mailing_form_valid(self):
        self.user.is_verified = True
        self.user.save()
        message = Message.objects.create(subject="Test Subject", body="Test Body", owner=self.user)
        client = MailClient.objects.create(
            email="client@example.com", full_name="Test Client", owner=self.user
        )
        form_data = {
            "start_datetime": timezone.now(),
            "periodicity": "daily",
            "status": "created",
            "message": message.id,
            "clients": [client.id],
        }
        form = MailingForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())


class EmailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client = MailClient.objects.create(
            email="client@example.com", full_name="Test Client", owner=self.user
        )
        self.message = Message.objects.create(
            subject="Test Subject", body="Test Body", owner=self.user
        )
        self.mailing = Mailing.objects.create(
            start_datetime=timezone.now(),
            periodicity="daily",
            status="created",
            message=self.message,
            owner=self.user,
        )
        self.mailing.clients.add(self.client)

    def test_send_mailing(self):
        from .tasks import send_mailing

        send_mailing()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test Subject")
        self.assertEqual(mail.outbox[0].body, "Test Body")
        self.assertEqual(mail.outbox[0].to, ["client@example.com"])

    def test_mailing_attempt_creation(self):
        from .tasks import send_mailing

        send_mailing()
        self.assertTrue(
            MailingAttempt.objects.filter(mailing=self.mailing, status="success").exists()
        )


class ManagerTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.manager = User.objects.create_user(
            username="manager", email="manager@example.com", password="manager123"
        )
        managers_group, _ = Group.objects.get_or_create(name="Managers")
        self.manager.groups.add(managers_group)

        # Create necessary permissions
        content_type = ContentType.objects.get_for_model(User)
        change_user_permission, _ = Permission.objects.get_or_create(
            content_type=content_type, codename="change_user", defaults={"name": "Can change user"}
        )
        managers_group.permissions.add(change_user_permission)

        # Add other necessary permissions
        mailing_content_type = ContentType.objects.get_for_model(Mailing)
        view_mailing_permission, _ = Permission.objects.get_or_create(
            content_type=mailing_content_type,
            codename="view_mailing",
            defaults={"name": "Can view mailing"},
        )
        managers_group.permissions.add(view_mailing_permission)

        self.manager.is_verified = True
        self.manager.save()

        self.client.login(email="manager@example.com", password="manager123")

    def test_manager_mailing_list_view(self):
        response = self.client.get(reverse("manager_mailing_list"))
        # print_debug_info(self, response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manager/mailing_list.html")

    def test_manager_user_list_view(self):
        response = self.client.get(reverse("manager_user_list"))
        # print_debug_info(self, response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manager/user_list.html")

    def test_manager_toggle_user(self):
        self.user.is_active = True
        self.user.save()

        response = self.client.post(reverse("manager_toggle_user", args=[self.user.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after toggle

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

        # Toggle back
        response = self.client.post(reverse("manager_toggle_user", args=[self.user.id]))
        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_manager_toggle_mailing(self):
        mailing = Mailing.objects.create(
            start_datetime=timezone.now(),
            periodicity="daily",
            status="created",
            message=Message.objects.create(subject="Test", body="Test", owner=self.user),
            owner=self.user,
        )
        response = self.client.get(reverse("manager_toggle_mailing", args=[mailing.id]))
        # print_debug_info(self, response)
        self.assertEqual(response.status_code, 302)  # Redirect after toggle
        mailing.refresh_from_db()
        self.assertEqual(mailing.status, "completed")
        mailing.refresh_from_db()
        self.assertEqual(mailing.status, "completed")
