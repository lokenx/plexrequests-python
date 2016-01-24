from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Movie
from django.contrib.auth.models import User


class MovieEndPointTests(APITestCase):
    def test_insertion_and_duplicate_movies(self):
        """
        Should insert new movie correctly but not allow
        duplicate movies to be inserted
        """
        user = User.objects.create(username='admin')
        client = APIClient()
        client.force_authenticate(user=user)
        data = { 'title': 'Test Movie', 'imdb': 'aa1234567890' }
        original_response = client.post('/api/movies/', data)
        duplicate_response = client.post('/api/movies/', data)
        self.assertEqual(original_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Movie.objects.get().imdb, 'aa1234567890')

    def test_retrieving_movie_list(self):
        """
        Should provide list of movie objects
        """
        user = User.objects.create(username='admin')
        Movie.objects.create(title='Test Movie', imdb='aa1234567890', requested_by=user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/movies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_deleting_movie(self):
        """
        Should delete an existing movie object
        """
        user = User.objects.create_superuser(username='admin', email='admin@doamin.com', password='secret')
        Movie.objects.create(title='Test Movie', imdb='aa1234567890', requested_by=user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.delete('/api/movies/1/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_updating_movie(self):
        """
        Should update an existing movie object
        """
        user = User.objects.create_superuser(username='admin', email='admin@doamin.com', password='secret')
        Movie.objects.create(title='Test Movie', imdb='aa1234567890', requested_by=user)
        client = APIClient()
        client.force_authenticate(user=user)
        data = { 'approved': 'true' }
        response = client.patch('/api/movies/1/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,
                         {'downloaded': False, 'approved': True, 'id': 1, 'imdb': 'aa1234567890',
                          'year': 0, 'pending': True, 'requested_by': 'admin',
                          'title': 'Test Movie', 'poster_path': ''})