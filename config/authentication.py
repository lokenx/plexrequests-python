import base64
import requests
import logging

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_jwt.serializers import JSONWebTokenSerializer, jwt_payload_handler, jwt_encode_handler
from xml.etree import ElementTree
from .models import Config


logger = logging.getLogger(__name__)


def plex_authentication(username, password):
    """
    Handle user login and registrations. Refer to issue #2 (https://github.com/lokenx/plex_requests/issues/2) for
    logic behind this

    :param username: user supplied username
    :param password: user supplied password
    :return: valid user object or None
    """
    try:
        # Check if user is an existing user
        user = User.objects.get(username=username)
        is_valid = user.check_password(password)
    except User.DoesNotExist:
        # If not an existing user check with Plex
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
                        logger.info('A new account was created for {}'.format(username))
                        return User.objects.create_user(username=username, email=email, password=password), None

        # If not a valid user or not on the friends list return None
        logger.warn("The user {} attempted to login, but failed Plex.tv verification or isn't on your friends list".format(username))
        return None

    if is_valid:
        # If an existing user confirm password is correct and return user, otherwise None
        return user, None
    else:
        logger.warn('The user {} attempted to login, but failed password verification'.format(username))
        return None


class CustomJWTSerializer(JSONWebTokenSerializer):
    """
    Custom validation/serialization for getting a JWT token
    """
    def validate(self, attrs):
        username = attrs.get('username').lower()
        password = attrs.get('password')

        user = plex_authentication(username=username, password=password)

        if user:
            if not user[0].is_active:
                logger.warn('The user {} attempted to login, but their account is disabled'.format(username))
                msg = 'User account is disabled.'
                raise serializers.ValidationError(msg)

            payload = jwt_payload_handler(user[0])

            return {
                'token': jwt_encode_handler(payload)
            }
        else:
            msg = 'Unable to login with provided credentials.'
            raise serializers.ValidationError(msg)
