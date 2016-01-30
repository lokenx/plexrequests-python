from rest_framework import serializers
from .models import Config


class ConfigSerializer(serializers.ModelSerializer):
    singleton_enforce = serializers.IntegerField(read_only=True)

    class Meta:
        model = Config
        fields = ('site_title', 'site_tagline', 'singleton_enforce')
        lookup_field = 'singleton__enforce'