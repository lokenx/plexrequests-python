from config.models import Config
from config.serializers import ConfigSerializer
from rest_framework import generics, permissions

class ConfigList(generics.RetrieveUpdateAPIView):
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer
    lookup_field = 'singleton_enforce'
    permission_classes = (permissions.IsAdminUser,)