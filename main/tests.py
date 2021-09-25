import json
import tempfile

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.test import TestCase, Client, override_settings

from main.models import Vendor, Consumer, Organization, Campaign, Outlet, Coupon, Interest, Type, Category

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class UserTestCase(StaticLiveServerTestCase):
    def _create_image(self):
        from PIL import Image

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            image = Image.new('RGB', (200, 200), 'white')
            image.save(f, 'PNG')

        return open(f.name, mode='rb')

    def setUp(self):
        self.client = Client()
        self.path = "/api/accounts/create"
        self.image = self._create_image()

    def check_data_code(self, path, data, code):
        for sample in data:
            response = self.client.post(path, sample)
            self.assertEqual(response.status_code, code)

    def test_creating_vendor(self):
        response = self.client.post(self.path, {
            "username": "test",
            "password": "Testik123",
            "email": "test@gmail.com",
            "atype": "V"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(Vendor.objects.count(), 1)
        user = get_user_model().objects.get()
        vendor = Vendor.objects.get()
        self.assertTupleEqual(
            (
                user.username,
                user.email,
                user.atype,
                user.vendor,
            ),
            (
                "test",
                "test@gmail.com",
                "V",
                vendor
            )
        )
        self.assertTupleEqual(
            (
                vendor.verified,
                vendor.user
            ),
            (
                False,
                user
            )
        )

    def test_creating_consumer(self):
        response = self.client.post(self.path, {
            "email": "test@gmail.com",
            "atype": "C"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(Consumer.objects.count(), 1)
        user = get_user_model().objects.get()
        consumer = Consumer.objects.get()
        self.assertTupleEqual(
            (
                user.username,
                user.email,
                user.atype,
                user.consumer
            ),
            (
                "test@gmail.com",
                "test@gmail.com",
                "C",
                consumer
            )
        )

    def test_field_omit(self):
        data = [
            {
                "password": "testik123",
                "email": "test@gmail.com",
                "atype": "V"
            },
            {
                "username": "test",
                "email": "test@gmail.com",
                "atype": "V"
            },
            {
                "username": "test",
                "password": "testik123",
                "atype": "V"
            },
            {
                "username": "test",
                "password": "testik123",
                "email": "test@gmail.com",
            },
            {
                "atype": "C"
            }
        ]
        self.check_data_code(self.path, data, 400)

    def test_wrong_field(self):
        data = [
            {
                "username": "test&*#!&$(*#!#()",
                "password": "testik123",
                "email": "test@gmail.com",
                "atype": "V"
            },
            {
                "username": "test",
                "password": "testik",
                "email": "test@gmail.com",
                "atype": "V"
            },
            {
                "username": "test",
                "password": "testik123",
                "email": "test",
                "atype": "V"
            },
            {
                "email": "test.com",
                "atype": "C"
            },
            {
                "email": "test@gmail.com",
                "atype": "jfadfjw"
            }
        ]
        self.check_data_code(self.path, data, 400)

    def test_non_unique_vendor(self):
        self.client.post(self.path, {
            "username": "test",
            "password": "Testik123",
            "email": "test@gmail.com",
            "atype": "V"
        })
        data = [
            {
                "username": "test",
                "password": "Testik123",
                "email": "test@gmail.com",
                "atype": "V"
            },
            {
                "username": "test1",
                "password": "Testik123",
                "email": "test@gmail.com",
                "atype": "V"
            },
            {
                "username": "test",
                "password": "Testik123",
                "email": "test1@gmail.com",
                "atype": "V"
            },
            {
                "email": "test@gmail.com",
                "atype": "C"
            },
        ]
        self.check_data_code(self.path, data, 400)

    def test_send_pin(self):
        self.client.post(self.path, {
            "email": "test@gmail.com",
            "atype": "C"
        })
        response = self.client.post("/api/accounts/send-pin", {
            "email": "test@gmail.com"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["test@gmail.com"])

    def test_send_pin_to_vendor(self):
        self.client.post(self.path, {
            "email": "test@gmail.com",
            "username": "test",
            "password": "Testik123",
            "atype": "V"
        })
        # Clear vendor verification email
        mail.outbox.clear()
        response = self.client.post("/api/accounts/send-pin", {
            "email": "test@gmail.com"
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)

    def test_verification_email(self):
        self.client.post(self.path, {
            "email": "vendor@gmail.com",
            "username": "vendor",
            "password": "Vendor123",
            "atype": "V"
        })
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["vendor@gmail.com"])
        mail.outbox.clear()
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.get("/api/accounts/send-verification-email", HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["vendor@gmail.com"])

    def test_restriction(self):
        self.client.post(self.path, {
            "email": "vendor@gmail.com",
            "username": "vendor",
            "password": "Vendor123",
            "atype": "V"
        })
        vendor = get_user_model().objects.get()
        vendor.vendor.verified = True
        vendor.vendor.restricted = True
        vendor.vendor.save()
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.post("/api/organizations", {
            "name": "McDonald's",
            "address": "London, Baker Street 221B"
        }, HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 403)
        vendor.vendor.restricted = False
        vendor.vendor.save()
        response = self.client.post("/api/organizations", {
            "name": "McDonald's",
            "address": "London, Baker Street 221B"
        }, HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 201)
        vendor.vendor.restricted = True
        vendor.vendor.save()
        organization = Organization.objects.get()
        organization.verified = True
        organization.save()
        response = self.client.post("/api/outlets", {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 403)
        response = self.client.post("/api/campaigns", {
            "organization": organization.id,
            "name": "Summer campaign",
            "start": "2001-11-15T19:15",
            "end": "2019-11-15T19:15"
        }, HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 403)
        vendor.vendor.restricted = False
        vendor.vendor.save()
        response = self.client.post("/api/outlets", {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 201)
        response = self.client.post("/api/campaigns", {
            "organization": organization.id,
            "name": "Summer campaign",
            "start": "2001-11-15T19:15",
            "end": "2019-11-15T19:15"
        }, HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 201)
        vendor.vendor.restricted = True
        vendor.vendor.save()
        outlet = Outlet.objects.get()
        campaign = Campaign.objects.get()
        interest = Interest.objects.create(name="IT", description="Informatics Techologies")
        ctype = Type.objects.create(name="Percentage", description="50% off")
        category = Category.objects.create(name="Opening", description="Coupons in new shops")
        response = self.client.post("/api/coupons", {
            "ctype": ctype.id,
            "category": category.id,
            "campaign": campaign.id,
            "outlets": [outlet.id],
            "name": "Best Sale!",
            "description": "Shop opening sale!",
            "deal": "Every item just half price",
            "image": self.image,
            "TC": "TC",
            "amount": 100,
            "code": "TE189312F",
            "start": "2001-11-15T10:00:00Z",
            "end": "2100-11-15T10:00:00Z",
            "advertisement": False,
            "active": False,
            "published": False,
            "interests": [interest.id]
        }, HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 403)
        vendor.vendor.restricted = False
        vendor.vendor.save()
        self.image = self._create_image()
        response = self.client.post("/api/coupons", {
            "ctype": ctype.id,
            "category": category.id,
            "campaign": campaign.id,
            "outlets": [outlet.id],
            "name": "Best Sale!",
            "description": "Shop opening sale!",
            "deal": "Every item just half price",
            "image": self.image,
            "TC": "TC",
            "amount": 100,
            "code": "TE189312F",
            "start": "2001-11-15T10:00:00Z",
            "end": "2100-11-15T10:00:00Z",
            "advertisement": False,
            "active": False,
            "published": False,
            "interests": [interest.id]
        }, HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 201)


class TokenTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.post("/api/accounts/create", {
            "username": "vendor",
            "email": "vendor@gmail.com",
            "password": "Vendor123",
            "atype": "V"
        })
        self.client.post("/api/accounts/create", {
            "email": "consumer@gmail.com",
            "atype": "C"
        })
        self.consumer = get_user_model().objects.filter(atype="C").get()
        self.vendor = get_user_model().objects.filter(atype="V").get()

    def test_vendor_token(self):
        # Creation
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor@gmail.com",
            "password": "Vendor123"
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.get("/api/accounts/vendor", {}, HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 200)

        # Verifying
        response = self.client.post("/api/accounts/token/verify", {
            "token": token
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue("token" in data)
        self.assertEqual(data["token"], token)

        # Refreshing
        response = self.client.post("/api/accounts/token/refresh", {
            "token": token
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue("token" in data)
        token = data["token"]
        response = self.client.get("/api/accounts/vendor", HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 200)

    def test_consumer_token(self):
        # Creating
        pin = self.consumer._set_new_pin()
        response = self.client.post("/api/accounts/token/get", {
            "email": "consumer@gmail.com",
            "password": pin
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.get("/api/accounts/consumer", HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 200)

        # Verifying
        response = self.client.post("/api/accounts/token/verify", {
            "token": token
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue("token" in data)
        self.assertEqual(data["token"], token)

        # Refreshing
        response = self.client.post("/api/accounts/token/refresh", {
            "token": token
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue("token" in data)
        token = data["token"]
        response = self.client.get("/api/accounts/consumer", HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 200)

    def test_wrong_data(self):
        data = [
            {
                "email": "consumer@gmail.com",
                "password": "WrongPassword"
            },
            {
                "email": "vendor@gmail.com",
                "password": "WrongPassword"
            },
            {
                "email": "consumer@gmail.com",
            },
            {
                "email": "vendor@gmail.com",
            }
        ]
        for sample in data:
            response = self.client.post("/api/accounts/token/get", sample)
            self.assertEqual(response.status_code, 400)

    def test_wrong_token(self):
        response = self.client.post("/api/accounts/token/refresh", {
            "token": "WrongToken"
        })
        self.assertEqual(response.status_code, 400)
        response = self.client.post("/api/accounts/token/verify", {
            "token": "WrongToken"
        })
        self.assertEqual(response.status_code, 400)


class TestOrganization(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.post("/api/accounts/create", {
            "username": "vendor",
            "email": "vendor@gmail.com",
            "password": "Vendor123",
            "atype": "V"
        })
        self.client.post("/api/accounts/create", {
            "email": "consumer@gmail.com",
            "atype": "C"
        })
        self.consumer = get_user_model().objects.filter(atype="C").get()
        self.vendor = get_user_model().objects.filter(atype="V").get()
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        self.token = data["token"]
        self.path = "/api/organizations"

    def test_creating_organization(self):
        self.vendor.vendor.verified = True
        self.vendor.vendor.save()
        response = self.client.post(self.path, {
            "name": "McDonald's",
            "address": "London, Baker street 221B"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Organization.objects.count(), 1)
        organization = Organization.objects.get()
        self.assertEqual(organization.vendor, self.vendor.vendor)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        response = self.client.get("{}/{}".format(self.path, organization.id))
        self.assertEqual(response.status_code, 200)

    def test_wrong_creating(self):
        # No token
        response = self.client.post(self.path, {
            "name": "Donald's",
            "address": "London, Baker street 221B"
        })
        self.assertEqual(response.status_code, 401)

        # Wrong token
        response = self.client.post(self.path, {
            "name": "Donald's",
            "address": "London, Baker street 221B"
        }, HTTP_AUTHORIZATION="JWT {}".format("WrongToken"))
        self.assertEqual(response.status_code, 401)

        # Not verified
        response = self.client.post(self.path, {
            "name": "Donald's",
            "address": "London, Baker street 221B"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 403)

        self.vendor.vendor.verified = True
        self.vendor.vendor.save()

        # Field omitted
        response = self.client.post(self.path, {
            "name": "Donald's",
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.path, {
            "address": "London, Baker street 221B"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        # Consumer tries to create
        pin = self.consumer._set_new_pin()
        response = self.client.post("/api/accounts/token/get", {
            "email": "consumer@gmail.com",
            "password": pin
        })
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.post(self.path, {
            "name": "Donald's",
            "address": "London, Baker street 221B"
        }, HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 403)

    def test_patching_organization(self):
        self.vendor.vendor.verified = True
        self.vendor.vendor.save()
        self.client.post(self.path, {
            "name": "McDonald's",
            "address": "London, Baker street 221B"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        organization = Organization.objects.get()
        response = self.client.patch("{}/{}".format(self.path, organization.id), json.dumps({
            "name": "KFC",
            "address": "USA, White House"
        }), HTTP_AUTHORIZATION="JWT {}".format(self.token), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTupleEqual(
            (
                data["name"],
                data["address"]
            ),
            (
                "KFC",
                "USA, White House"
            )
        )

    def test_deleting_organization(self):
        self.vendor.vendor.verified = True
        self.vendor.vendor.save()
        self.client.post(self.path, {
            "name": "McDonald's",
            "address": "London, Baker street 221B"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        organization = Organization.objects.get()
        response = self.client.delete("{}/{}".format(self.path, organization.id),
                                      HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Organization.objects.count(), 0)

    def test_wrong_patching(self):
        self.vendor.vendor.verified = True
        self.vendor.vendor.save()
        self.client.post("/api/accounts/create", {
            "username": "vendor2",
            "email": "vendor2@gmail.com",
            "password": "Vendor123",
            "atype": "V"
        })
        self.client.post(self.path, {
            "name": "McDonald's",
            "address": "London, Baker street 221B"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123"
        })

        # Access denied
        data = json.loads(response.content)
        token = data["token"]
        organization = Organization.objects.get()
        response = self.client.patch("{}/{}".format(self.path, organization.id), json.dumps({
            "name": "KFC",
            "address": "USA, White House"
        }), HTTP_AUTHORIZATION="JWT {}".format(token), content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # No credentials
        response = self.client.patch("{}/{}".format(self.path, organization.id), json.dumps({
            "name": "KFC",
            "address": "USA, White House"
        }))
        self.assertEqual(response.status_code, 401)

        # Already verified
        organization.verified = True
        organization.save()
        response = self.client.patch("{}/{}".format(self.path, organization.id), json.dumps({
            "name": "KFC",
            "address": "USA, White House"
        }), HTTP_AUTHORIZATION="JWT {}".format(self.token), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_wrong_deleting(self):
        self.vendor.vendor.verified = True
        self.vendor.vendor.save()
        self.client.post("/api/accounts/create", {
            "username": "vendor2",
            "email": "vendor2@gmail.com",
            "password": "Vendor123",
            "atype": "V"
        })
        self.client.post(self.path, {
            "name": "McDonald's",
            "address": "London, Baker street 221B"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))

        # Access denied
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        token = data["token"]
        organization = Organization.objects.get()
        response = self.client.delete("{}/{}".format(self.path, organization.id),
                                      HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 403)

        # No credentials
        response = self.client.delete("{}/{}".format(self.path, organization.id))
        self.assertEqual(response.status_code, 401)


class CampaignTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.post("/api/accounts/create", {
            "email": "vendor@gmail.com",
            "username": "vendor",
            "password": "Vendor123",
            "atype": "V"
        })
        self.client.post("/api/accounts/create", {
            "email": "consumer@gmail.com",
            "atype": "C"
        })
        self.vendor = get_user_model().objects.filter(atype="V").get()
        self.consumer = get_user_model().objects.filter(atype="C").get()
        self.vendor.vendor.verified = True
        self.vendor.vendor.save()
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        self.token = data["token"]
        self.client.post("/api/organizations", {
            "name": "McDonald's",
            "address": "London, Baker street 221B"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.organization = self.vendor.vendor.organization
        self.path = "/api/campaigns"

    def test_campaign_creating(self):
        self.organization.verified = True
        self.organization.save()
        response = self.client.post(self.path, {
            "organization": self.organization.id,
            "name": "Summer campaign",
            "start": "2001-11-15T19:15",
            "end": "2019-11-15T19:15"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Campaign.objects.count(), 1)
        campaign = Campaign.objects.get()
        self.assertEqual(campaign.organization, self.organization)
        response = self.client.get("{}/{}".format(self.path, campaign.id))
        self.assertEqual(response.status_code, 200)

    def test_wrong_creating(self):
        # No token
        response = self.client.post(self.path, {
            "organization": self.organization.id,
            "name": "Summer campaign",
            "start": "2001-11-15T19:15",
            "end": "2019-11-15T19:15"
        })
        self.assertEqual(response.status_code, 401)

        # Wrong token
        response = self.client.post(self.path, {
            "organization": self.organization.id,
            "name": "Summer campaign",
            "start": "2001-11-15T19:15",
            "end": "2019-11-15T19:15"
        })
        self.assertEqual(response.status_code, 401)

        # Not verified
        response = self.client.post(self.path, {
            "organization": self.organization.id,
            "name": "Summer campaign",
            "start": "2001-11-15T19:15",
            "end": "2019-11-15T19:15"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        self.organization.verified = True
        self.organization.save()

        # Field omitted
        response = self.client.post(self.path, {
            "name": "Summer campaign",
            "start": "2001-11-15T19:15",
            "end": "2019-11-15T19:15"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)
        response = self.client.post(self.path, {
            "organization": self.organization.id,
            "start": "2001-11-15T19:15",
            "end": "2019-11-15T19:15"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)
        response = self.client.post(self.path, {
            "organization": self.organization.id,
            "name": "Summer campaign",
            "end": "2019-11-15T19:15"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)
        response = self.client.post(self.path, {
            "organization": self.organization.id,
            "name": "Summer campaign",
            "start": "2001-11-15T19:15",
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        # Access to organization denied
        user = get_user_model().objects.create_user(username="test", email="test@gmail.com",
                                                    password="test12345", atype="V")
        vendor = user.vendor
        organization = Organization.objects.create(name="KFC", address="USA, White House", vendor=vendor)
        response = self.client.post(self.path, {
            "organization": organization.id,
            "name": "Summer campaign",
            "start": "2001-11-15T19:15",
            "end": "2019-11-15T19:15"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        # Wrong fields
        response = self.client.post(self.path, {
            "organization": self.organization.id,
            "name": "Summer campaign",
            "start": "blah-blah-blah",
            "end": "2019-11-15T19:15"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)
        response = self.client.post(self.path, {
            "organization": self.organization.id,
            "name": "Summer campaign",
            "start": "2001-11-15T19:15",
            "end": "blah-blah-blah"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)
        response = self.client.post(self.path, {
            "organization": 0,
            "name": "Summer campaign",
            "start": "2001-11-15T19:15",
            "end": "2019-11-15T19:15"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

    def test_patching_campaign(self):
        self.organization.verified = True
        self.organization.save()
        path = "/api/campaigns"
        self.client.post(path, {
            "organization": self.organization.id,
            "name": "Summer campaign",
            "start": "2018-06-01T00:00",
            "end": "2018-09-01T00:00"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        campaign = Campaign.objects.get()
        response = self.client.patch("{}/{}".format(path, campaign.id), json.dumps({
            "name": "Winter campaign",
            "start": "2018-12-01T00:00",
            "end": "2018-03-01T00:00"
        }), HTTP_AUTHORIZATION="JWT {}".format(self.token), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTupleEqual(
            (
                data["name"],
                data["start"],
                data["end"]
            ),
            (
                "Winter campaign",
                "2018-12-01T00:00:00Z",
                "2018-03-01T00:00:00Z"
            )
        )

    def test_deleting_campaign(self):
        self.organization.verified = True
        self.organization.save()
        path = "/api/campaigns"
        self.client.post(path, {
            "organization": self.organization.id,
            "name": "Summer campaign",
            "start": "2018-06-01T00:00",
            "end": "2018-09-01T00:00"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        campaign = Campaign.objects.get()
        response = self.client.delete("{}/{}".format(path, campaign.id), HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Campaign.objects.count(), 0)

    def test_wrong_patching(self):
        self.organization.verified = True
        self.organization.save()
        path = "/api/campaigns"
        self.client.post(path, {
            "organization": self.organization.id,
            "name": "Summer campaign",
            "start": "2018-06-01T00:00",
            "end": "2018-09-01T00:00"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        campaign = Campaign.objects.get()

        # No credentials
        response = self.client.patch("{}/{}".format(path, campaign.id), json.dumps({
            "name": "Winter campaign",
            "start": "2018-12-01T00:00",
            "end": "2018-03-01T00:00"
        }), content_type='application/json')
        self.assertEqual(response.status_code, 401)

        # Access denied
        self.client.post("/api/accounts/create", {
            "username": "vendor2",
            "email": "vendor2@gmail.com",
            "password": "Vendor123",
            "atype": "V"
        })
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.patch("{}/{}".format(path, campaign.id), json.dumps({
            "name": "Winter campaign",
            "start": "2018-12-01T00:00",
            "end": "2018-03-01T00:00"
        }), HTTP_AUTHORIZATION="JWT {}".format(token), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.patch("{}/{}".format(path, campaign.id), json.dumps({
            "name": "Winter campaign",
            "start": "2018-12-01T00:00",
            "end": "2018-03-01T00:00"
        }), HTTP_AUTHORIZATION="JWT {}".format(token), content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # Wrong fields
        response = self.client.patch("{}/{}".format(path, campaign.id), json.dumps({
            "name": "Winter campaign",
            "start": "blah-blah-blah",
            "end": "2018-03-01T00:00"
        }), HTTP_AUTHORIZATION="JWT {}".format(self.token), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = self.client.patch("{}/{}".format(path, campaign.id), json.dumps({
            "name": "Winter campaign",
            "start": "2018-12-01T00:00",
            "end": "blah-blah-blah"
        }), HTTP_AUTHORIZATION="JWT {}".format(self.token), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_wrong_deleting(self):
        self.organization.verified = True
        self.organization.save()
        path = "/api/campaigns"
        self.client.post(path, {
            "organization": self.organization.id,
            "name": "Summer campaign",
            "start": "2018-06-01T00:00",
            "end": "2018-09-01T00:00"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        campaign = Campaign.objects.get()

        # No authorization
        response = self.client.delete("{}/{}".format(path, campaign.id))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Campaign.objects.count(), 1)

        # No access
        self.client.post("/api/accounts/create", {
            "username": "vendor2",
            "email": "vendor2@gmail.com",
            "password": "Vendor123",
            "atype": "V"
        })
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.delete("{}/{}".format(path, campaign.id), HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Campaign.objects.count(), 1)


class TestOutlet(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.post("/api/accounts/create", {
            "email": "vendor@gmail.com",
            "username": "vendor",
            "password": "Vendor123",
            "atype": "V"
        })
        self.client.post("/api/accounts/create", {
            "email": "consumer@gmail.com",
            "atype": "C"
        })
        self.vendor = get_user_model().objects.filter(atype="V").get()
        self.consumer = get_user_model().objects.filter(atype="C").get()
        self.vendor.vendor.verified = True
        self.vendor.vendor.save()
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        self.token = data["token"]
        self.client.post("/api/organizations", {
            "name": "McDonald's",
            "address": "London, Baker street 221B"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.organization = self.vendor.vendor.organization
        self.path = "/api/outlets"

    def test_outlet_creating(self):
        self.organization.verified = True
        self.organization.save()
        response = self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Outlet.objects.count(), 1)
        outlet = Outlet.objects.get()
        response = self.client.get("{}/{}".format(self.path, outlet.id))
        self.assertEqual(response.status_code, 200)

    def test_wrong_creating(self):
        # No credentials
        response = self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": self.organization.id
        })
        self.assertEqual(response.status_code, 401)

        # Organization not verified
        response = self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        # Wrong credentials
        response = self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format("Wrong token"))
        self.assertEqual(response.status_code, 401)

        self.organization.verified = True
        self.organization.save()

        # Field omitted
        response = self.client.post(self.path, {
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.path, {
            "name": "McDonald's in London",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "longitude": "-0.118092",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        # Wrong data
        response = self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "blah-blah-blah",
            "longitude": "-0.118092",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "blah-blah-blah",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": "blah-blah-blah"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        # Access denied
        self.client.post("/api/accounts/create", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123",
            "username": "vendor2",
            "atype": "V"
        })
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 400)

    def test_patching_outlet(self):
        self.organization.verified = True
        self.organization.save()
        self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        outlet = Outlet.objects.get()
        response = self.client.patch("{}/{}".format(self.path, outlet.id), json.dumps({
            "name": "KFC in Boston",
            "description": "Just more one KFC",
            "address": "Boston",
            "latitude": "42.361145",
            "longitude": "-71.057083"
        }), HTTP_AUTHORIZATION="JWT {}".format(self.token), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("{}/{}".format(self.path, outlet.id))
        o = json.loads(response.content)
        self.assertTupleEqual(
            (
                o["name"],
                o["description"],
                o["address"],
                o["latitude"],
                o["longitude"]
            ),
            (
                "KFC in Boston",
                "Just more one KFC",
                "Boston",
                42.361145,
                -71.057083
            )
        )

    def test_deleting_outlet(self):
        self.organization.verified = True
        self.organization.save()
        self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        outlet = Outlet.objects.get()
        response = self.client.delete("{}/{}".format(self.path, outlet.id),
                                      HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Outlet.objects.count(), 0)

    def test_wrong_patching(self):
        self.organization.verified = True
        self.organization.save()
        self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        outlet = Outlet.objects.get()

        # No auth
        response = self.client.patch("{}/{}".format(self.path, outlet.id), json.dumps({
            "name": "KFC in Boston",
            "description": "Just more one KFC",
            "address": "Boston",
            "latitude": "42.361145",
            "longitude": "-71.057083"
        }), content_type="application/json")
        self.assertEqual(response.status_code, 401)

        # Wrong auth
        response = self.client.patch("{}/{}".format(self.path, outlet.id), json.dumps({
            "name": "KFC in Boston",
            "description": "Just more one KFC",
            "address": "Boston",
            "latitude": "42.361145",
            "longitude": "-71.057083"
        }), HTTP_AUTHORIZATION="JWT {}".format("Wrong token"), content_type="application/json")
        self.assertEqual(response.status_code, 401)

        # Wrong data
        response = self.client.patch("{}/{}".format(self.path, outlet.id), json.dumps({
            "name": "KFC in Boston",
            "description": "Just more one KFC",
            "address": "Boston",
            "latitude": "blah-blah-blah",
            "longitude": "-71.057083"
        }), HTTP_AUTHORIZATION="JWT {}".format(self.token), content_type="application/json")
        self.assertEqual(response.status_code, 400)

        response = self.client.patch("{}/{}".format(self.path, outlet.id), json.dumps({
            "name": "KFC in Boston",
            "description": "Just more one KFC",
            "address": "Boston",
            "latitude": "42.361145",
            "longitude": "blah-blah-blah"
        }), HTTP_AUTHORIZATION="JWT {}".format(self.token), content_type="application/json")
        self.assertEqual(response.status_code, 400)

        # Access denied
        self.client.post("/api/accounts/create", {
            "username": "vendor2",
            "email": "vendor2@gmail.com",
            "password": "Vendor123",
            "atype": "V"
        })
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.patch("{}/{}".format(self.path, outlet.id), json.dumps({
            "name": "KFC in Boston",
            "description": "Just more one KFC",
            "address": "Boston",
            "latitude": "42.361145",
            "longitude": "-71.057083"
        }), HTTP_AUTHORIZATION="JWT {}".format(token), content_type="application/json")
        self.assertEqual(response.status_code, 403)

    def test_wrong_deleting(self):
        self.organization.verified = True
        self.organization.save()
        self.client.post(self.path, {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        outlet = Outlet.objects.get()

        # No auth
        response = self.client.delete("{}/{}".format(self.path, outlet.id))
        self.assertEqual(response.status_code, 401)
        # Wrong auth
        response = self.client.delete("{}/{}".format(self.path, outlet.id),
                                      HTTP_AUTHORIZATION="JWT {}".format("Wrong token"))
        self.assertEqual(response.status_code, 401)

        # Access denied
        self.client.post("/api/accounts/create", {
            "username": "vendor2",
            "email": "vendor2@gmail.com",
            "password": "Vendor123",
            "atype": "V"
        })
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.delete("{}/{}".format(self.path, outlet.id),
                                      HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 403)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestCoupon(StaticLiveServerTestCase):
    def _create_image(self):
        from PIL import Image

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            image = Image.new('RGB', (200, 200), 'white')
            image.save(f, 'PNG')

        return open(f.name, mode='rb')

    def setUp(self):
        self.client = Client()
        self.client.post("/api/accounts/create", {
            "email": "vendor@gmail.com",
            "username": "vendor",
            "password": "Vendor123",
            "atype": "V"
        })
        self.client.post("/api/accounts/create", {
            "email": "consumer@gmail.com",
            "atype": "C"
        })
        self.vendor = get_user_model().objects.filter(atype="V").get()
        self.consumer = get_user_model().objects.filter(atype="C").get()
        self.vendor.vendor.verified = True
        self.vendor.vendor.save()
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        self.token = data["token"]
        self.client.post("/api/organizations", {
            "name": "McDonald's",
            "address": "London, Baker street 221B"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.organization = self.vendor.vendor.organization
        self.organization.verified = True
        self.organization.save()
        self.client.post("/api/outlets", {
            "name": "McDonald's in London",
            "description": "Just more one McDonald's",
            "address": "London",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "organization": self.organization.id
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.outlet = Outlet.objects.get()
        self.client.post("/api/campaigns", {
            "organization": self.organization.id,
            "name": "Summer campaign",
            "start": "2001-11-15T19:15",
            "end": "2019-11-15T19:15"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.campaign = Campaign.objects.get()
        self.interest = Interest.objects.create(name="IT", description="Informatics Techologies")
        self.ctype = Type.objects.create(name="Percentage", description="50% off")
        self.category = Category.objects.create(name="Opening", description="Coupons in new shops")
        self.path = "/api/coupons"
        self.image = self._create_image()

    def test_coupon_creating(self):
        response = self.client.post(self.path, {
            "ctype": self.ctype.id,
            "category": self.category.id,
            "campaign": self.campaign.id,
            "outlets": [self.outlet.id],
            "name": "Best Sale!",
            "description": "Shop opening sale!",
            "deal": "Every item just half price",
            "image": self.image,
            "TC": "TC",
            "amount": 100,
            "code": "TE189312F",
            "start": "2001-11-15T10:00:00Z",
            "end": "2100-11-15T10:00:00Z",
            "advertisement": False,
            "active": False,
            "published": False,
            "interests": [self.interest.id]
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Coupon.objects.count(), 1)
        coupon = Coupon.objects.get()
        response = self.client.get("{}/{}".format(self.path, coupon.id))
        self.assertEqual(response.status_code, 200)

    def test_wrong_creating(self):
        # No auth
        response = self.client.post(self.path, {
            "ctype": self.ctype.id,
            "category": self.category.id,
            "campaign": self.campaign.id,
            "outlets": [self.outlet.id],
            "name": "Best Sale!",
            "description": "Shop opening sale!",
            "deal": "Every item just half price",
            "image": self.image,
            "TC": "TC",
            "amount": 100,
            "code": "TE189312F",
            "start": "2001-11-15T10:00:00Z",
            "end": "2100-11-15T10:00:00Z",
            "advertisement": False,
            "active": False,
            "published": False,
            "interests": [self.interest.id]
        })
        self.assertEqual(response.status_code, 401)

        # Wrong auth
        response = self.client.post(self.path, {
            "ctype": self.ctype.id,
            "category": self.category.id,
            "campaign": self.campaign.id,
            "outlets": [self.outlet.id],
            "name": "Best Sale!",
            "description": "Shop opening sale!",
            "deal": "Every item just half price",
            "image": self.image,
            "TC": "TC",
            "amount": 100,
            "code": "TE189312F",
            "start": "2001-11-15T10:00:00Z",
            "end": "2100-11-15T10:00:00Z",
            "advertisement": False,
            "active": False,
            "published": False,
            "interests": [self.interest.id]
        }, HTTP_AUTHORIZATION="JWT {}".format("Wrong token"))
        self.assertEqual(response.status_code, 401)

        # Wrong data.
        response = self.client.post(self.path, {
            "ctype": 0,
            "category": self.category.id,
            "campaign": self.campaign.id,
            "outlets": [self.outlet.id],
            "name": "Best Sale!",
            "description": "Shop opening sale!",
            "deal": "Every item just half price",
            "image": self.image,
            "TC": "TC",
            "amount": 100,
            "code": "TE189312F",
            "start": "2001-11-15T10:00:00Z",
            "end": "2100-11-15T10:00:00Z",
            "interests": [self.interest.id]
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.path, {
            "ctype": self.ctype.id,
            "category": self.category.id,
            "campaign": self.campaign.id,
            "outlets": [0],
            "name": "Best Sale!",
            "description": "Shop opening sale!",
            "deal": "Every item just half price",
            "image": self.image,
            "TC": "TC",
            "amount": 100,
            "code": "TE189312F",
            "start": "2001-11-15T10:00:00Z",
            "end": "2100-11-15T10:00:00Z",
            "interests": [self.interest.id]
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.path, {
            "ctype": self.ctype.id,
            "category": self.category.id,
            "campaign": self.campaign.id,
            "outlets": [self.outlet.id],
            "name": "Best Sale!",
            "description": "Shop opening sale!",
            "deal": "Every item just half price",
            "image": "blah-blah-blah",
            "TC": "TC",
            "amount": 100,
            "code": "TE189312F",
            "start": "2001-11-15T10:00:00Z",
            "end": "2100-11-15T10:00:00Z",
            "interests": [self.interest.id]
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.path, {
            "ctype": self.ctype.id,
            "category": self.category.id,
            "campaign": self.campaign.id,
            "outlets": [self.outlet.id],
            "name": "Best Sale!",
            "description": "Shop opening sale!",
            "deal": "Every item just half price",
            "image": self.image,
            "TC": "TC",
            "amount": -1,
            "code": "TE189312F",
            "start": "2001-11-15T10:00:00Z",
            "end": "2100-11-15T10:00:00Z",
            "interests": [self.interest.id]
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.path, {
            "ctype": self.ctype.id,
            "category": self.category.id,
            "campaign": self.campaign.id,
            "outlets": [self.outlet.id],
            "name": "Best Sale!",
            "description": "Shop opening sale!",
            "deal": "Every item just half price",
            "image": self.image,
            "TC": "TC",
            "amount": 100,
            "code": "TE189312F",
            "start": "blah-blah-blah",
            "end": "blah-blah-blah",
            "interests": [self.interest.id]
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(self.path, {
            "ctype": self.ctype.id,
            "category": self.category.id,
            "campaign": self.campaign.id,
            "outlets": [self.outlet.id],
            "name": "Best Sale!",
            "description": "Shop opening sale!", "deal": "Every item just half price",
            "image": self.image,
            "TC": "TC",
            "amount": 100,
            "code": "TE189312F",
            "start": "2001-11-15T10:00:00Z",
            "end": "2100-11-15T10:00:00Z",
            "interests": [-1]
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 400)

        # Access to campaign denied
        self.client.post("/api/accounts/create", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123",
            "username": "vendor2",
            "atype": "V"
        })
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.post(self.path, {
            "ctype": self.ctype.id,
            "category": self.category.id,
            "campaign": self.campaign.id,
            "outlets": [self.outlet.id],
            "name": "Best Sale!",
            "description": "Shop opening sale!",
            "deal": "Every item just half price",
            "image": self.image,
            "TC": "TC",
            "amount": 100,
            "code": "TE189312F",
            "start": "2001-11-15T10:00:00Z",
            "end": "2100-11-15T10:00:00Z",
            "advertisement": False,
            "active": False,
            "published": False,
            "interests": [self.interest.id]
        }, HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 400)

    def test_patching_coupons(self):
        response = self.client.post(self.path, {
            "ctype": self.ctype.id,
            "category": self.category.id,
            "campaign": self.campaign.id,
            "outlets": [self.outlet.id],
            "name": "Best Sale!",
            "description": "Shop opening sale!",
            "deal": "Every item just half price",
            "image": self.image,
            "TC": "TC",
            "amount": 100,
            "code": "TE189312F",
            "start": "2001-11-15T10:00:00Z",
            "end": "2100-11-15T10:00:00Z",
            "advertisement": False,
            "active": False,
            "published": False,
            "interests": [self.interest.id]
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        coupon = Coupon.objects.get()
        header = {"HTTP_X_HTTP_METHOD_OVERRIDE": "PATCH"}
        response = self.client.post("{}/{}".format(self.path, coupon.id), {
            "name": "New name",
            "description": "New description",
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token), **header)
        self.assertEqual(response.status_code, 200)
        response = self.client.get("{}/{}".format(self.path, coupon.id))
        data = json.loads(response.content)
        self.assertTupleEqual(
            (
                data["name"],
                data["description"]
            ),
            (
                "New name",
                "New description"
            )
        )

    def test_deleting_coupons(self):
        self.client.post(self.path, {
            "ctype": self.ctype.id,
            "category": self.category.id,
            "campaign": self.campaign.id,
            "outlets": [self.outlet.id],
            "name": "Best Sale!",
            "description": "Shop opening sale!",
            "deal": "Every item just half price",
            "image": self.image,
            "TC": "TC",
            "amount": 100,
            "code": "TE189312F",
            "start": "2001-11-15T10:00:00Z",
            "end": "2100-11-15T10:00:00Z",
            "advertisement": False,
            "active": False,
            "published": False,
            "interests": [self.interest.id]
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        coupon = Coupon.objects.get()
        response = self.client.delete("{}/{}".format(self.path, coupon.id),
                                      HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Coupon.objects.count(), 0)

    def test_wrong_patching(self):
        self.client.post(self.path, {
            "ctype": self.ctype.id,
            "category": self.category.id,
            "campaign": self.campaign.id,
            "outlets": [self.outlet.id],
            "name": "Best Sale!",
            "description": "Shop opening sale!",
            "deal": "Every item just half price",
            "image": self.image,
            "TC": "TC",
            "amount": 100,
            "code": "TE189312F",
            "start": "2001-11-15T10:00:00Z",
            "end": "2100-11-15T10:00:00Z",
            "advertisement": False,
            "active": False,
            "published": False,
            "interests": [self.interest.id]
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        header = {"HTTP_X_HTTP_METHOD_OVERRIDE": "PATCH"}
        coupon = Coupon.objects.get()
        data = [
            {
                "start": "blah-blah-blah"
            },
            {
                "end": "blah-blah-blah"
            },
            {
                "image": "blah-blah-blah"
            },
            {
                "ctype": 0
            },
            {
                "campaign": 0
            },
            {
                "category": 0
            },
            {
                "outlets": [0]
            },
            {
                "interests": [0]
            }
        ]
        for sample in data:
            response = self.client.post("{}/{}".format(self.path, coupon.id),
                                         sample,
                                         HTTP_AUTHORIZATION="JWT {}".format(self.token), **header)
            self.assertEqual(response.status_code, 400)

        # No auth
        response = self.client.post("{}/{}".format(self.path, coupon.id), {
            "name": "New name"
        }, **header)
        self.assertEqual(response.status_code, 401)

        # Wrong auth
        response = self.client.post("{}/{}".format(self.path, coupon.id), {
            "name": "New name"
        }, HTTP_AUTHORIZATION="JWT {}".format("Wrong token"), **header)
        self.assertEqual(response.status_code, 401)

        # Access denied
        self.client.post("/api/accounts/create", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123",
            "username": "vendor2",
            "atype": "V"
        })
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.post("{}/{}".format(self.path, coupon.id), {
            "name": "New name"
        }, HTTP_AUTHORIZATION="JWT {}".format(token), **header)
        self.assertEqual(response.status_code, 403)

    def test_wrong_deleting(self):
        self.client.post(self.path, {
            "ctype": self.ctype.id,
            "category": self.category.id,
            "campaign": self.campaign.id,
            "outlets": [self.outlet.id],
            "name": "Best Sale!",
            "description": "Shop opening sale!",
            "deal": "Every item just half price",
            "image": self.image,
            "TC": "TC",
            "amount": 100,
            "code": "TE189312F",
            "start": "2001-11-15T10:00:00Z",
            "end": "2100-11-15T10:00:00Z",
            "advertisement": False,
            "active": False,
            "published": False,
            "interests": [self.interest.id]
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        coupon = Coupon.objects.get()
        # No auth
        response = self.client.delete("{}/{}".format(self.path, coupon.id))
        self.assertEqual(response.status_code, 401)

        # Wrong auth
        response = self.client.delete("{}/{}".format(self.path, coupon.id),
                                      HTTP_AUTHORIZATION="JWT {}".format("Wrong token"))
        self.assertEqual(response.status_code, 401)

        # Access denied
        self.client.post("/api/accounts/create", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123",
            "username": "vendor2",
            "atype": "V"
        })
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.delete("{}/{}".format(self.path, coupon.id),
                                      HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 403)


class TestAdminFunctionality(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.post("/api/accounts/create", {
            "email": "vendor@gmail.com",
            "username": "vendor",
            "password": "Vendor123",
            "atype": "V"
        })
        self.client.post("/api/accounts/create", {
            "email": "consumer@gmail.com",
            "atype": "C"
        })
        self.vendor = get_user_model().objects.filter(atype="V").get()
        self.consumer = get_user_model().objects.filter(atype="C").get()
        self.vendor.vendor.verified = True
        self.vendor.is_staff = True
        self.vendor.is_superuser = True
        self.vendor.save()
        self.vendor.vendor.save()
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        self.token = data["token"]
        self.client.post("/api/organizations", {
            "name": "McDonald's",
            "address": "London, Baker street 221B"
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.organization = self.vendor.vendor.organization

    def test_grant_user(self):
        self.client.post("/api/accounts/create", {
            "username": "vendor2",
            "email": "vendor2@gmail.com",
            "password": "Vendor123",
            "atype": "V"
        })
        vendor2 = get_user_model().objects.get(username="vendor2")
        response = self.client.post("/api/admin/grant", {
            "id": vendor2.id,
            "state": True
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 200)
        vendor2 = get_user_model().objects.get(username="vendor2")
        self.assertTrue(vendor2.is_staff and vendor2.is_superuser)
        response = self.client.post("/api/admin/grant", {
            "id": vendor2.id,
            "state": False
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 200)
        vendor2 = get_user_model().objects.get(username="vendor2")
        self.assertFalse(vendor2.is_staff or vendor2.is_superuser)

    def test_verify_organization(self):
        response = self.client.post("/api/admin/verify", {
            "id": self.organization.id,
            "state": True
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 200)
        self.organization = Organization.objects.get()
        self.assertTrue(self.organization.verified)
        response = self.client.post("/api/admin/verify", {
            "id": self.organization.id,
            "state": False
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 200)
        self.organization = Organization.objects.get()
        self.assertFalse(self.organization.verified)

    def test_restrict_user(self):
        response = self.client.post("/api/admin/restrict", {
            "id": self.vendor.id,
            "state": True
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 200)
        self.vendor = get_user_model().objects.get(atype="V")
        self.assertTrue(self.vendor.vendor.restricted)
        response = self.client.post("/api/admin/restrict", {
            "id": self.vendor.id,
            "state": False
        }, HTTP_AUTHORIZATION="JWT {}".format(self.token))
        self.assertEqual(response.status_code, 200)
        self.vendor = get_user_model().objects.get(atype="V")
        self.assertFalse(self.vendor.vendor.restricted)

    def test_wrong_granting(self):
        # No auth
        response = self.client.post("/api/admin/grant", {
            "id": self.vendor.id,
            "state": True
        })
        self.assertEqual(response.status_code, 401)

        # Wrong auth
        response = self.client.post("/api/admin/grant", {
            "id": self.vendor.id,
            "state": True
        }, HTTP_AUTHORIZATION="JWT {}".format("Wrong token"))
        self.assertEqual(response.status_code, 401)

        # Access denied
        self.client.post("/api/accounts/create", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123",
            "username": "vendor2",
            "atype": "V"
        })
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.post("/api/admin/grant", {
            "id": self.vendor.id,
            "state": True
        }, HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 403)

    def test_wrong_verifying(self):
        # No auth
        response = self.client.post("/api/admin/verify", {
            "id": self.organization.id,
            "state": True
        })
        self.assertEqual(response.status_code, 401)

        # Wrong auth
        response = self.client.post("/api/admin/verify", {
            "id": self.organization.id,
            "state": True
        }, HTTP_AUTHORIZATION="JWT {}".format("Wrong token"))
        self.assertEqual(response.status_code, 401)

        # Access denied
        self.client.post("/api/accounts/create", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123",
            "username": "vendor2",
            "atype": "V"
        })
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.post("/api/admin/verify", {
            "id": self.organization.id,
            "state": True
        }, HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 403)

    def test_wrong_restricting(self):
        # No auth
        response = self.client.post("/api/admin/restrict", {
            "id": self.vendor.id,
            "state": True
        })
        self.assertEqual(response.status_code, 401)
        # Wrong auth
        response = self.client.post("/api/admin/restrict", {
            "id": self.vendor.id,
            "state": True
        }, HTTP_AUTHORIZATION="JWT {}".format("Wrong token"))
        self.assertEqual(response.status_code, 401)

        # Access denied
        self.client.post("/api/accounts/create", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123",
            "username": "vendor2",
            "atype": "V"
        })
        response = self.client.post("/api/accounts/token/get", {
            "email": "vendor2@gmail.com",
            "password": "Vendor123"
        })
        data = json.loads(response.content)
        token = data["token"]
        response = self.client.post("/api/admin/restrict", {
            "id": self.vendor.id,
            "state": True
        }, HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, 403)
