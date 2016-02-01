from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Config
from django.contrib.auth.models import User
import httpretty


class ConfigEndPointTests(APITestCase):
    def test_retrieving_config(self):
        """
        Should provide config object
        """
        user = User.objects.create_superuser(username='admin', email='admin@doamin.com', password='secret')
        Config.objects.create()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/settings/1/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_updating_config(self):
        """
        Should update config object
        """
        user = User.objects.create_superuser(username='admin', email='admin@doamin.com', password='secret')
        Config.objects.create()
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'site_title': 'New Title'}
        response = client.patch('/api/settings/1/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @httpretty.activate
    def test_new_plex_login(self):
        """
        Should log a new valid plex user in
        """
        httpretty.register_uri(httpretty.POST, "https://plex.tv/users/sign_in.json",
                               body='{"user":{"email": "test@email.com"}}',
                               status=201)

        httpretty.register_uri(httpretty.GET, "https://plex.tv/pms/friends/all?X-Plex-Token=abcd1234",
                               body="""<?xml version='1.0' encoding='UTF-8'?><MediaContainer>
                                    <User username='user' email='test@email.com'><Server/></User></MediaContainer>""",
                               status=200)

        Config.objects.create()
        client = APIClient()
        data = {'username': 'user', 'password': 'pass'}
        response = client.post('/api/login/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get().username, 'user')

    @httpretty.activate
    def test_invalid_plex_login(self):
        """
        Should reject an invalid new plex user
        """
        httpretty.register_uri(httpretty.POST, "https://plex.tv/users/sign_in.json",
                               body='Denied Access',
                               status=401)

        Config.objects.create()
        client = APIClient()
        data = {'username': 'user', 'password': 'pass'}
        response = client.post('/api/login/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    @httpretty.activate
    def test_invalid_plex_friend(self):
        """
        Should reject a valid new plex user that isn't friends with the server admin
        """
        httpretty.register_uri(httpretty.POST, "https://plex.tv/users/sign_in.json",
                               body='{"user":{"email": "test@email.com"}}',
                               status=201)

        httpretty.register_uri(httpretty.GET, "https://plex.tv/pms/friends/all?X-Plex-Token=abcd1234",
                               body="""<?xml version='1.0' encoding='UTF-8'?><MediaContainer>
                                    <User username='another' email='test@email.com'><Server/></User></MediaContainer>""",
                               status=200)

        Config.objects.create()
        client = APIClient()
        data = {'username': 'user', 'password': 'pass'}
        response = client.post('/api/login/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_existing_user(self):
        """
        Should login an existing user in the database
        """
        user = User.objects.create_superuser(username='admin', email='admin@doamin.com', password='secret')
        Config.objects.create()
        client = APIClient()
        valid_data = {'username': 'admin', 'password': 'secret'}
        invalid_data = {'username': 'admin', 'password': 'notsecret'}
        valid_response = client.post('/api/login/', valid_data)
        invalid_response = client.post('/api/login/', invalid_data)

        self.assertEqual(valid_response.status_code, status.HTTP_200_OK)
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_disabled_user(self):
        """
        Should reject a disabled user from logging in
        """
        user = User.objects.create_user(username='admin', email='admin@doamin.com', password='secret')
        user.is_active = False
        user.save()
        Config.objects.create()
        client = APIClient()
        data = {'username': 'admin', 'password': 'secret'}
        response = client.post('/api/login/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_password(self):
        """
        Should reject a login attempt without the username or password field
        """
        user = User.objects.create_user(username='admin', email='admin@doamin.com', password='secret')
        user.is_active = False
        user.save()
        Config.objects.create()
        client = APIClient()
        u_data = {'username': 'admin'}
        p_data = {'password': 'secret'}
        u_response = client.post('/api/login/', u_data)
        p_response = client.post('/api/login/', p_data)

        self.assertEqual(u_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(p_response.status_code, status.HTTP_400_BAD_REQUEST)
