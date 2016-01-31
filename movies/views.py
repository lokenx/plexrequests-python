import datetime
from django.utils import timezone

from movies.models import Movie
from movies.serializers import MovieSerializer
from rest_framework import generics, permissions, serializers
from config.models import Config

class MovieList(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        conf = Config.objects.get()

        today = timezone.now()
        week_ago = today - datetime.timedelta(days=7)
        requested_since = Movie.objects.filter(requested_by=self.request.user).filter(created__gte=week_ago).count()

        # If you're an admin user or approvals aren't required set to true
        # Also checks limits
        if self.request.user.is_staff or conf.requests_approval == False:
            serializer.save(requested_by=self.request.user, approved=True, pending=False)
        elif conf.limit_movie == 0 or requested_since < conf.limit_movie:
            serializer.save(requested_by=self.request.user, approved=False, pending=True)
        else:
            content = { 'error': "You've exceeded your weekly limit for movie requests" }
            raise serializers.ValidationError(content)


class MovieDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = (permissions.IsAdminUser,)
