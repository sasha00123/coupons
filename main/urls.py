from django.urls import path, include
from rest_framework_jwt.views import ObtainJSONWebToken, RefreshJSONWebToken, VerifyJSONWebToken

from main.serializers import CustomJWTSerializer
from main.views import send_pin, verify_email, ConsumerProfile, create_user, VendorProfile, UserInfoView, \
    resend_verification_email

token = [
    path('get', ObtainJSONWebToken.as_view(serializer_class=CustomJWTSerializer)),
    path('refresh', RefreshJSONWebToken.as_view()),
    path('verify', VerifyJSONWebToken.as_view()), path("vendor", VendorProfile.as_view()),
]

accounts = [
    path("create", create_user),
    path("info", UserInfoView.as_view()),
    path("send-pin", send_pin),
    path("send-verification-email", resend_verification_email),
    path("consumer", ConsumerProfile.as_view()),
    path("vendor", VendorProfile.as_view()),
    path("token/", include(token))
]

api = [
    path("accounts/", include(accounts)),
]

urlpatterns = [
    path("api/", include(api)),
    path("verify-email", verify_email),
]
