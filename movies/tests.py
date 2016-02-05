import httpretty
import json
import requests

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Movie
from config.models import Config
from django.contrib.auth.models import User

@httpretty.activate
class MovieEndPointTests(APITestCase):
    def test_insertion_and_duplicate_movies(self):
        """
        Should insert new movie correctly but not allow
        duplicate movies to be inserted
        """
        json_body = json.dumps({'imdb_id': 'aa1234567890' })
        httpretty.register_uri(httpretty.GET, 'https://api.themoviedb.org/3/movie/1', body=json_body)

        Config.objects.create()
        user = User.objects.create(username='admin')
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'title': 'Test Movie', 'imdb': 'aa1234567890', 'release_date': '2000-01-01', 'id': '1'}
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

        self.assertEqual(response.data['count'], 1)
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

        self.assertEqual(response.data, None)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_updating_movie(self):
        """
        Should update an existing movie object
        """
        user = User.objects.create_superuser(username='admin', email='admin@doamin.com', password='secret')
        Movie.objects.create(title='Test Movie', id=1, imdb='aa1234567890', release_date='2000-01-01', requested_by=user)
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'approved': 'true'}
        response = client.patch('/api/movies/1/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,
                         {'downloaded': False, 'approved': True, 'id': 1, 'imdb': 'aa1234567890',
                          'release_date': '2000-01-01', 'pending': True, 'requested_by': 'admin',
                          'title': 'Test Movie', 'poster_path': ''})

    @httpretty.activate
    def test_movie_limits(self):
        """
        Should fail insert new movie due to limit
        """
        json_body = json.dumps({'imdb_id': 'aa1234567890' })
        httpretty.register_uri(httpretty.GET, 'https://api.themoviedb.org/3/movie/1', body=json_body)

        Config.objects.create(limit_movie=1, requests_approval=True)
        user = User.objects.create(username='admin')
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'title': 'Test Movie', 'imdb': 'aa1234567890', 'release_date': '2000-01-01', 'id': '1'}
        data_2 = {'title': 'Test Movie', 'imdb': 'bb1234567890', 'release_date': '2000-01-01', 'id': '1'}
        first_response = client.post('/api/movies/', data)
        second_response = client.post('/api/movies/', data_2)

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)

    @httpretty.activate
    def test_couchpotato_add(self):
        """
        Should successfully add a movie to CouchPotato
        """
        json_body = json.dumps({'imdb_id': 'aa1234567890' })
        httpretty.register_uri(httpretty.GET, 'https://api.themoviedb.org/3/movie/1', body=json_body)

        json_body_2 = json.dumps({'success': True})
        httpretty.register_uri(httpretty.GET, "http://192.168.0.1:5050/api/abcd1234/movie.add?identifier=aa1234567890",
                               body=json_body_2,
                               content_type="application/json",
                               status=200)

        Config.objects.create(couchpotato_enabled=True)
        user = User.objects.create(username='admin')
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'title': 'Test Movie', 'imdb': 'aa1234567890', 'release_date': '2000-01-01', 'id': '1'}
        response = client.post('/api/movies/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.get().approved, True)

    @httpretty.activate
    def test_couchpotato_fail(self):
        """
        Should fail to add a movie to CouchPotato
        """
        json_body = json.dumps({'imdb_id': 'aa1234567890' })
        httpretty.register_uri(httpretty.GET, 'https://api.themoviedb.org/3/movie/1', body=json_body)

        json_body_2 = json.dumps({'success': False})
        httpretty.register_uri(httpretty.GET, "http://192.168.0.1:5050/api/abcd1234/movie.add?identifier=aa1234567890",
                               body=json_body_2,
                               content_type="application/json",
                               status=200)

        Config.objects.create(couchpotato_enabled=True)
        user = User.objects.create(username='admin')
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'title': 'Test Movie', 'imdb': 'aa1234567890', 'release_date': '2000-01-01', 'id': '1'}
        response = client.post('/api/movies/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.get().approved, False)

    @httpretty.activate
    def test_couchpotato_timeout(self):
        """
        Should fail to add due to a timeout
        """

        def exception_callback(request, uri, headers):
            raise requests.Timeout('Connection timed out.')

        json_body = json.dumps({'imdb_id': 'aa1234567890' })
        httpretty.register_uri(httpretty.GET, 'https://api.themoviedb.org/3/movie/1', body=json_body)

        httpretty.register_uri(httpretty.GET,
                               "http://192.168.0.1:5050/api/abcd1234/movie.add?identifier=aa1234567890",
                               body=exception_callback)

        Config.objects.create(couchpotato_enabled=True)
        user = User.objects.create(username='admin')
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'title': 'Test Movie', 'imdb': 'aa1234567890', 'release_date': '2000-01-01', 'id': '1'}
        response = client.post('/api/movies/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.get().approved, False)
