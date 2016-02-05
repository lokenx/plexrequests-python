import datetime
import logging
import tmdbsimple as tmdb

from django.conf import settings
from helpers import couchpotato
from django.utils import timezone
from movies.models import Movie
from movies.serializers import MovieSerializer
from rest_framework import generics, permissions, serializers
from config.models import Config

tmdb.API_KEY = settings.TMDB_API
logger = logging.getLogger(__name__)


class MovieList(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        conf = Config.objects.get()

        # Try and get IMDB ID
        response = tmdb.Movies(self.request.data['id']).info()

        if not response['imdb_id']:
            logger.warn('No IMDB could be found for {}'.format(self.request.data['title']))
            content = {'error': 'No IMDB ID could be found, please open an issue'}
            raise serializers.ValidationError(content)

        today = timezone.now()
        week_ago = today - datetime.timedelta(days=7)
        requested_since = Movie.objects.filter(requested_by=self.request.user).filter(created__gte=week_ago).count()

        # If you're an admin user or approvals aren't required set to true, also checks limits
        if self.request.user.is_staff or conf.requests_approval is False:
            if conf.couchpotato_enabled:
                add_movie = couchpotato.add(self.request.data['imdb'])

                if add_movie:
                    logger.info(
                        'The user {} requested {} ({}) and was automatically approved and added to CouchPotato'.format(
                            self.request.user, self.request.data['title'], self.request.data['release_date']))
                    serializer.save(requested_by=self.request.user, imdb=response['imdb_id'], approved=True,
                                    pending=False)
                elif add_movie is False:
                    logger.warn(
                        'The user {} requested {} ({}) but could not be added to CouchPotato'.format(self.request.user,
                                                                                                     self.request.data[
                                                                                                         'title'],
                                                                                                     self.request.data[
                                                                                                         'release_date']))
                    serializer.save(requested_by=self.request.user, imdb=response['imdb_id'], approved=False,
                                    pending=True)
                else:
                    logger.warn(
                        'The user {} requested {} ({}) but could not connect to CouchPotato'.format(self.request.user,
                                                                                                    self.request.data[
                                                                                                        'title'],
                                                                                                    self.request.data[
                                                                                                        'release_date']))
                    serializer.save(requested_by=self.request.user, imdb=response['imdb_id'], approved=False,
                                    pending=True)
            else:
                logger.info(
                    'The user {} requested {} ({}) and was automatically approved'.format(
                        self.request.user, self.request.data['title'], self.request.data['release_date']))
                serializer.save(requested_by=self.request.user, imdb=response['imdb_id'], approved=True, pending=False)

        elif conf.limit_movie == 0 or requested_since < conf.limit_movie:
            logger.info('The user {} requested {} ({})'.format(self.request.user, self.request.data['title'],
                                                               self.request.data['release_date']))
            serializer.save(requested_by=self.request.user, imdb=response['imdb_id'], approved=False, pending=True)
        else:
            logger.info('{} requested a movie beyond their weekly limit.'.format(self.request.user))
            content = {'error': "You've exceeded your weekly limit for movie requests"}
            raise serializers.ValidationError(content)


class MovieDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = (permissions.IsAdminUser,)
