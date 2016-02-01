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
