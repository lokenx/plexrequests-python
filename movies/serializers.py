from rest_framework import serializers
from movies.models import Movie

class MovieSerializer(serializers.ModelSerializer):
    requested_by = serializers.ReadOnlyField(source='requested_by.username')

    class Meta:
        model = Movie
        fields = ('id', 'title', 'release_date', 'id', 'imdb', 'downloaded', 'poster_path', 'approved', 'pending',
                  'requested_by')