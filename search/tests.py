import httpretty
import json

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from config.models import Config


class SearchEndPointTests(APITestCase):
    @httpretty.activate
    def test_movie_search(self):
        """
        Should retrieve list of movie search results
        """
        json_body = json.dumps({
            "page": 1,
            "results": [
                {
                  "adult": False,
                  "backdrop_path": "/8uO0gUM8aNqYLs1OsTBQiXu0fEv.jpg",
                  "genre_ids": [
                    18
                  ],
                  "id": 550,
                  "original_language": "en",
                  "original_title": "Fight Club",
                  "overview": "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male",
                  "release_date": "1999-10-14",
                  "poster_path": "/811DjJTon9gD6hZ8nCjSitaIXFQ.jpg",
                  "popularity": 4.39844,
                  "title": "Fight Club",
                  "video": False,
                  "vote_average": 7.8,
                  "vote_count": 3527
                }
            ]
        })

        httpretty.register_uri(httpretty.GET,
                               "https://api.themoviedb.org/3/search/movie",
                               body=json_body,
                               content_type='application/json'
                               )

        Config.objects.create()
        user = User.objects.create(username='admin')
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/search?type=movie&query=dark')

        self.assertEqual(response.data[0]['title'], 'Fight Club')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_incorrect_search(self):
        """
        Should give an error if type or query is missing or incorrect
        """
        Config.objects.create()
        user = User.objects.create(username='admin')
        client = APIClient()
        client.force_authenticate(user=user)
        first_response = client.get('/api/search?type=movie&query=')
        second_response = client.get('/api/search?type=&query=dark')
        third_response = client.get('/api/search?type=dark&query=dark')

        self.assertEqual(first_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(third_response.status_code, status.HTTP_400_BAD_REQUEST)