from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_jwt.serializers import JSONWebTokenSerializer, jwt_payload_handler, jwt_encode_handler


def custom_authentication_thing(username, password):
    try:
        user = User.objects.get(username=username)
        is_valid = user.check_password(password)
    except User.DoesNotExist:
        # This is where I check against Plex and create account if they're valid
        return None

    if is_valid:
        return user, None
    else:
        return None


class CustomJWTSerializer(JSONWebTokenSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = custom_authentication_thing(username=username, password=password)

            if user:
                if not user[0].is_active:
                    msg = 'User account is disabled.'
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user[0])

                return {
                    'token': jwt_encode_handler(payload)
                }
            else:
                msg = 'Unable to login with provided credentials.'
                raise serializers.ValidationError(msg)
        else:
            msg = 'Must include "username" and "password"'
            raise serializers.ValidationError(msg)
