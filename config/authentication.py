import base64
import requests

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_jwt.serializers import JSONWebTokenSerializer, jwt_payload_handler, jwt_encode_handler
from xml.etree import ElementTree
from .models import Config


def plex_authentication(username, password):
    try:
        user = User.objects.get(username=username)
        is_valid = user.check_password(password)
    except User.DoesNotExist:
        # This is where I check against Plex and create account if they're valid
        # Check the user is a valid Plex user
        base64_auth = base64.encodestring(('%s:%s' % (username,password)).encode()).decode().replace('\n', '')

        headers = {
            'Authorization': 'Basic ' + base64_auth,
            'X-Plex-Client-Identifier': 'BLS6IF8NV9OX3LHGIG9G63WIGO',
            'X-Plex-Version': '0.1.0',
            'X-Plex-Platform': 'Python',
            'X-Plex-Device-Name': 'Plex Requests'
        }
        check_plex_login = requests.post('https://plex.tv/users/sign_in.json', headers=headers)

        if check_plex_login.status_code == 201:
            email = check_plex_login.json()['user']['email']
            conf = Config.objects.get()
            token = conf.auth_plextoken
            friends_list = requests.get('https://plex.tv/pms/friends/all?X-Plex-Token=%s' % token)

            # If valid user confirm they're on the friends list of server admin
            if friends_list.status_code == 200:
                tree = ElementTree.fromstring(friends_list.text)
                for user in tree.findall('User'):
                    if username == user.get('username'):
                        return User.objects.create_user(username=username, email=email, password=password), None

        return None

    if is_valid:
        return user, None
    else:
        return None


class CustomJWTSerializer(JSONWebTokenSerializer):
    def validate(self, attrs):
        username = attrs.get('username').lower()
        password = attrs.get('password')

        if username and password:
            user = plex_authentication(username=username, password=password)

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
