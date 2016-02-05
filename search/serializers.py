from rest_framework import serializers


class MovieResultsSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    release_date = serializers.DateField()
    overview = serializers.CharField(max_length=1000)
    poster_path = serializers.CharField(max_length=255)
    id = serializers.CharField(max_length=255)
