from random import randint
from urllib.parse import urlencode, quote_plus

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
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

    REQUIRED_FIELDS = ['atype', 'username1']
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

    coupons_rated = models.ManyToManyField('Coupon', related_name="consumers_rated",
                                           related_query_name="consumer_rated",
                                           through='Rate')
    coupons_short_listed = models.ManyToManyField('Coupon', related_name="consumers_short_listed",
                                                  related_query_name="consumer_short_listed",
                                                  through='ShortList')
    coupons_used = models.ManyToManyField('Coupon', related_name="consumers_used", related_query_name="consumer_used")

    interests = models.ManyToManyField('Interest', related_name="consumers", related_query_name="consumer")

    def __str__(self):
        return self.full_name or ''


class Vendor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    verified = models.BooleanField(blank=True, default=False)
    restricted = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return str(self.id) or ''


class Organization(models.Model):
    # If migrate to multiple organizations - change to ForeignKeyField
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name="organization",
                                  related_query_name="organization")

    name = models.TextField(unique=True)
    address = models.TextField()

    verified = models.BooleanField(blank=True, default=False)
    reviewed = models.BooleanField(blank=True, default=False)

    def get_owner(self):
        return self.vendor.user

    def __str__(self):
        return self.name or ''


class Campaign(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="campaigns",
                                     related_query_name="campaign")

    name = models.TextField()

    start = models.DateTimeField()
    end = models.DateTimeField()

    active = models.BooleanField(default=False)

    def get_owner(self):
        return self.organization.get_owner()

    def __str__(self):
        return self.name or ''


class Outlet(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="outlets",
                                     related_query_name="outlet")

    name = models.TextField()
    description = models.TextField()

    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    geom = PointField(blank=True)

    def get_owner(self):
        return self.organization.get_owner()

    def save(self, *args, **kwargs):
        self.geom = Point(self.latitude, self.longitude)
        super(Outlet, self).save(*args, **kwargs)

    def __str__(self):
        return self.name or ''


class Coupon(models.Model):
    ctype = models.ForeignKey('Type', on_delete=models.CASCADE, related_name="coupons",
                              related_query_name="coupon")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="coupons",
                                 related_query_name="coupon")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="coupons",
                                 related_query_name="coupon")
    outlets = models.ManyToManyField(Outlet, related_name="coupons", related_query_name="coupon")

    name = models.TextField()
    description = models.TextField()
    deal = models.TextField()
    image = models.ImageField(upload_to='coupons/images/')

    TC = models.TextField()
    amount = models.IntegerField()
    code = models.TextField()

    start = models.DateTimeField()
    end = models.DateTimeField()

    advertisement = models.BooleanField(blank=True, default=True)
    active = models.BooleanField(blank=True, default=True)
    published = models.BooleanField(blank=True, default=False)

    interests = models.ManyToManyField('Interest', related_name="coupons", related_query_name="coupon")

    def get_owner(self):
        return self.campaign.get_owner()

    def __str__(self):
        return self.name or ''


class Type(models.Model):
    name = models.TextField()
    description = models.TextField()


class Category(models.Model):
    name = models.TextField()
    description = models.TextField()


class Rate(models.Model):
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    rate = models.IntegerField()
    review = models.TextField(blank=True, null=True)


class ShortList(models.Model):
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    active = models.BooleanField(blank=True, default=True)


class Use(models.Model):
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)


class Interest(models.Model):
    name = models.TextField()
    description = models.TextField()
