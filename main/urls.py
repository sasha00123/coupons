from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import ObtainJSONWebToken, RefreshJSONWebToken, VerifyJSONWebToken

from main.serializers import CustomJWTSerializer
from main.views import send_pin, verify_email, ConsumerProfile, OrganizationViewSet, create_user, \
    CampaignViewSet, OutletViewSet, CouponViewSet, VendorProfile, CategoryListView, TypeListView, InterestListView, \
    UserInfoView, resend_verification_email, grant_admin, verify_organization, restrict

router = DefaultRouter(trailing_slash=False)
router.register(r'organizations', OrganizationViewSet, base_name='organization')
router.register(r'campaigns', CampaignViewSet, base_name='campaign')
router.register(r'outlets', OutletViewSet, base_name='outlet')
router.register(r'coupons', CouponViewSet, base_name='coupon')
router.register(r'categories', CategoryListView, base_name='category')
router.register(r'types', TypeListView, base_name='type')
router.register(r'interests', InterestListView, base_name='interest')

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
admin = [
    path("restrict", restrict),
    path("grant", grant_admin),
    path("verify", verify_organization)
]
api = [
    path("", include(router.urls)),
    path("accounts/", include(accounts)),
    path("admin/", include(admin))
]
urlpatterns = [
    path("api/", include(api)),
    path("verify-email", verify_email),
]
