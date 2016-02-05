import tmdbsimple as tmdb
import logging

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from search.serializers import MovieResultsSerializer

tmdb.API_KEY = settings.TMDB_API
logger = logging.getLogger(__name__)


@api_view(['GET'])
def search_request(request):
    type = request.GET.get('type') or None
    query = request.GET.get('query') or None

    if not type or not query:
        return Response(data={'error': 'Please specify a type and query url parameters'}, status=status.HTTP_400_BAD_REQUEST)

    if type == 'movie':
        search = tmdb.Search()
        response = search.movie(query=query)
        results = MovieResultsSerializer(search.results, many=True)

        return Response(data=results.data, status=status.HTTP_200_OK)
    else:
        return Response(data={'error': 'Incorrect search type provided'}, status=status.HTTP_400_BAD_REQUEST)