from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import status, viewsets, exceptions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from simple_email_confirmation.exceptions import EmailConfirmationExpired

from main.models import Organization, Campaign, Outlet, Coupon, Category, Type, Interest
from main.permissions import IsVendor, IsConsumer, IsAdminUserOrReadOnly, IsOwnerOrReadOnly, \
    IsEmailVerifiedOrReadOnly, IsAdmin, IsNotRestricted
from main.serializers import UserSerializer, ConsumerSerializer, OrganizationSerializer, CampaignSerializer, \
    OutletSerializer, CouponSerializer, VendorSerializer, CategorySerializer, TypeSerializer, InterestSerializer, \
    RetrieveCouponSerializer, RetriveUpdateUserSerializer, VendorStateSerializer, OrganizationStateSerializer


@api_view(['POST'])
def create_user(request: Request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        if user:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def send_pin(request: Request):
    email = request.data["email"]
    try:
        user = get_user_model().objects.get(email=email, atype="C")
        message, stat = user.send_pin()
    except get_user_model().DoesNotExist:
        return Response("No user with such email", status=status.HTTP_400_BAD_REQUEST)
    return Response(message, status=stat)


def verify_email(request):
    if not "email" in request.GET or not "code" in request.GET:
        return HttpResponse("Broken link!".format(request.GET))
    email, code = request.GET["email"], request.GET["code"]
    try:
        user = get_user_model().objects.get(email=email, atype="V")
    except get_user_model().DoesNotExist:
        return HttpResponse("Wrong email!")
    try:
        user.confirm_email(code)
        user.vendor.verified = True
        user.vendor.save()
    except EmailConfirmationExpired:
        return HttpResponse("Code expired!")
    except:
        return HttpResponse("Wrong code!")
    return HttpResponse("OK<br><a href='/'>Home</a>")


class ConsumerProfile(APIView):
    permission_classes = [IsAuthenticated, IsConsumer]

    def get(self, request: Request):
        profile = request.user.consumer
        serializer = ConsumerSerializer(profile)
        return Response(serializer.data)

    def patch(self, request: Request):
        profile = request.user.consumer
        serializer = ConsumerSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            profile = serializer.save()
            if profile:
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorProfile(APIView):
    permission_classes = [IsAuthenticated, IsVendor]

    def get(self, request: Request):
        profile = request.user.vendor
        serializer = VendorSerializer(profile)
        response = serializer.data
        response["coupons"] = [CouponSerializer(coupon).data for coupon in
                               Coupon.objects.filter(campaign__organization__vendor=profile)]
        response["campaigns"] = [CampaignSerializer(campaign).data for campaign in
                                 Campaign.objects.filter(organization__vendor=profile)]
        response["outlets"] = [OutletSerializer(outlet).data for outlet in
                                Outlet.objects.filter(organization__vendor=profile)]
        return Response(response)

    def patch(self, request: Request):
        profile = request.user.vendor
        serializer = VendorSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            profile = serializer.save()
            if profile:
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MethodSerializerView(object):
    """
    Utility class for get different serializer class by method.
    For example:
    method_serializer_classes = {
        ('GET', ): MyModelListViewSerializer,
        ('PUT', 'PATCH'): MyModelCreateUpdateSerializer
    }
    """
    method_serializer_classes = None

    def get_serializer_class(self):
        assert self.method_serializer_classes is not None, (
                'Expected view %s should contain method_serializer_classes '
                'to get right serializer class.' %
                (self.__class__.__name__,)
        )
        for methods, serializer_cls in self.method_serializer_classes.items():
            if self.request.method in methods:
                return serializer_cls

        raise exceptions.MethodNotAllowed(self.request.method)


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, IsEmailVerifiedOrReadOnly, IsNotRestricted]
    queryset = Organization.objects.all()


class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, IsNotRestricted]
    queryset = Campaign.objects.all()


class OutletViewSet(viewsets.ModelViewSet):
    serializer_class = OutletSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, IsNotRestricted]
    queryset = Outlet.objects.all()


class CouponViewSet(MethodSerializerView, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, IsNotRestricted]
    parser_classes = (MultiPartParser, FormParser)
    queryset = Coupon.objects.all()
    method_serializer_classes = {
        ('GET',): RetrieveCouponSerializer,
        ('POST', 'PATCH'): CouponSerializer,
    }

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        request.method = request.META.get("HTTP_X_HTTP_METHOD_OVERRIDE", request.POST.get("_method", request.method)).upper()
        return request


class CategoryListView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = Category.objects.all()


class TypeListView(viewsets.ModelViewSet):
    serializer_class = TypeSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = Type.objects.all()


class InterestListView(viewsets.ModelViewSet):
    serializer_class = InterestSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = Interest.objects.all()


class UserInfoView(generics.RetrieveUpdateAPIView):
    serializer_class = RetriveUpdateUserSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    queryset = get_user_model().objects.all()

    def get_object(self):
        return self.queryset.get(pk=self.request.user.pk)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsVendor])
def resend_verification_email(request: Request):
    request.user.send_verification_email()
    return Response("OK", status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def grant_admin(request: Request):
    data = VendorStateSerializer(data=request.data)
    if data.is_valid():
        user = data.validated_data["id"]
        state = data.validated_data["state"]
        user.is_staff, user.is_superuser = state, state
        user.save()
        return Response("OK", status=status.HTTP_200_OK)
    return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def verify_organization(request: Request):
    data = OrganizationStateSerializer(data=request.data)
    if data.is_valid():
        organization = data.validated_data["id"]
        state = data.validated_data["state"]
        organization.verified = state
        organization.review = True
        organization.save()
        return Response("OK", status=status.HTTP_200_OK)
    return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def restrict(request: Request):
    data = VendorStateSerializer(data=request.data)
    if data.is_valid():
        user = data.validated_data["id"]
        state = data.validated_data["state"]
        user.vendor.restricted = state
        user.vendor.save()
        return Response("OK", status=status.HTTP_200_OK)
    return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)
