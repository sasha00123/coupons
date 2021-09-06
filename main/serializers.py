import re

from django.contrib.auth import get_user_model, authenticate
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_jwt.serializers import JSONWebTokenSerializer, jwt_payload_handler, jwt_encode_handler

from main.models import Consumer, Vendor


class CustomJWTSerializer(JSONWebTokenSerializer):
    username_field = 'email'

    def validate(self, attrs: dict):
        password = attrs.get("password")
        user_obj = get_user_model().objects.filter(email=attrs.get("email")).first()
        if user_obj is not None:
            credentials = {
                'username': user_obj.email,
                'password': password
            }
            if all(credentials.values()):
                user = authenticate(**credentials)
                if user:
                    if not user.is_active:
                        msg = 'User account is disabled.'
                        raise serializers.ValidationError(msg)

                    payload = jwt_payload_handler(user)

                    return {
                        'token': jwt_encode_handler(payload),
                        'user': user
                    }
                else:
                    msg = 'Unable to log in with provided credentials.'
                    raise serializers.ValidationError(msg)

            else:
                msg = 'Must include "{username_field}" and "password".'
                msg = msg.format(username_field=self.username_field)
                raise serializers.ValidationError(msg)

        else:
            msg = 'Account with this email does not exists'
            raise serializers.ValidationError(msg)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=32,
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[
            UniqueValidator(queryset=get_user_model().objects.all()),
            RegexValidator(re.compile(r'^[\w.-]+$'), "Enter a valid username.")
        ]
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=get_user_model().objects.all()),
        ]
    )
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'password', 'atype')

    def create(self, validated_data: dict):
        user = super(UserSerializer, self).create(validated_data)
        if validated_data['atype'] == 'V':
            user.set_password(validated_data['password'])
        else:
            user.set_unusable_password()
        user.save()
        return user

    def validate(self, data: dict):
        if data['atype'] == 'V':
            if 'password' not in data or not data['password']:
                raise serializers.ValidationError("Vendor must have a password")
            if len(data['password']) < 8:
                raise serializers.ValidationError("Password must has at least 8 characters")
            if 'username' not in data or not data['username']:
                raise serializers.ValidationError("Vendor must have a username!")
        else:
            data['username'] = data['email']
        return data


class ConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer
        fields = ['full_name', 'birth_date']


class VendorSerializer(serializers.ModelSerializer):
    verified = serializers.BooleanField(read_only=True)
    restricted = serializers.BooleanField(read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Vendor
        fields = ['verified', 'organization', 'restricted', 'email']


class RetriveUpdateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=32,
        validators=[
            UniqueValidator(queryset=get_user_model().objects.all()),
            RegexValidator(re.compile(r'^[\w.-]+$'), "Enter a valid username.")
        ],
        required=False,
        allow_null=True,
        allow_blank=True
    )
    email = serializers.EmailField(read_only=True)
    password = serializers.CharField(write_only=True, required=False, min_length=8, allow_null=True, allow_blank=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'password')

    def update(self, user: get_user_model(), validated_data: dict):
        if 'password' in validated_data and validated_data['password']:
            user.set_password(validated_data["password"])
        if 'username' in validated_data and validated_data['username']:
            user.username = validated_data["username"]
        user.save()
        return user
