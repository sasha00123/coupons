from random import randint
from urllib.parse import urlencode, quote_plus

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import get_template
from rest_framework import status
from simple_email_confirmation.models import SimpleEmailConfirmationUserMixin


class User(SimpleEmailConfirmationUserMixin, AbstractUser):
    ACCOUNT_TYPES = [
        ("V", "Vendor"),
        ("C", "Consumer")
    ]

    atype = models.TextField(choices=ACCOUNT_TYPES)
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = [atype]
    USERNAME_FIELD = 'email'

    def send_verification_email(self):
        payload = {'email': self.email, 'code': self.get_confirmation_key()}
        result = urlencode(payload, quote_via=quote_plus)
        d = {'result': result, 'site_url': settings.SITE_URL}
        subject, from_email, to = "Email verification", "no-reply@example.com", self.email
        text_content = get_template("main/email/email-confirmation.txt").render(d)
        html_content = get_template("main/email/email-confirmation.html").render(d)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def save(self, *args, **kwargs):
        created = self.pk is None
        super(User, self).save(*args, **kwargs)
        if created:
            if self.atype == "V":
                Vendor.objects.create(user=self)
                self.send_verification_email()
            else:
                Consumer.objects.create(user=self)

    def _send_pin_email(self, pin: str):
        d = {'username': self.username, 'pin': pin}
        subject, from_email, to = "New PIN", "no-reply@example.com", self.email
        text_content = get_template("main/email/new-pin.txt").render(d)
        html_content = get_template("main/email/new-pin.html").render(d)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def _set_new_pin(self) -> str:
        pin = hex(randint(16 ** 4, 16 ** 5 - 1))[2:]
        self.set_password(pin)
        self.save()
        return pin

    def send_pin(self):
        if self.atype != "C":
            return "Cannot send pin to a vendor!", status.HTTP_400_BAD_REQUEST
        self._send_pin_email(self._set_new_pin())
        return "PIN was sent", status.HTTP_200_OK

    def __str__(self):
        return self.username or ''


class Consumer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    full_name = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.full_name or ''


class Vendor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    verified = models.BooleanField(blank=True, default=False)
    restricted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return str(self.id) or ''
