import json
import tempfile

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.test import TestCase, Client, override_settings

from main.models import Vendor, Consumer

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
        print(response.content)
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
        print(response.content)
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
