from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from simple_email_confirmation.exceptions import EmailConfirmationExpired

from main.permissions import IsVendor, IsConsumer
from main.serializers import UserSerializer, ConsumerSerializer, VendorSerializer, RetriveUpdateUserSerializer


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


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsVendor])
def resend_verification_email(request: Request):
    request.user.send_verification_email()
    return Response("OK", status=status.HTTP_200_OK)


def verify_email(request):
    if "email" not in request.GET or "code" not in request.GET:
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
        return Response(response)

    def patch(self, request: Request):
        profile = request.user.vendor
        serializer = VendorSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            profile = serializer.save()
            if profile:
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(generics.RetrieveUpdateAPIView):
    serializer_class = RetriveUpdateUserSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    queryset = get_user_model().objects.all()

    def get_object(self):
        return self.queryset.get(pk=self.request.user.pk)
