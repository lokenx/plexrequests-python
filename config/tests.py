from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Config
from django.contrib.auth.models import User


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
        data = { 'site_title': 'New Title' }
        response = client.patch('/api/settings/1/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)