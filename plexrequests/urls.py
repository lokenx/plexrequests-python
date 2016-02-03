from django.conf.urls import url, include, patterns
from django.contrib import admin

from config.authentication import CustomJWTSerializer
from movies import views as movie_views
from config import views as config_views
from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework_jwt.views import refresh_jwt_token


# Add url root if set by user
try:
    root_url_file = open('plexrequests/root_url.txt', 'r')
    root_url = root_url_file.read()
except IOError:
    root_url = ''

if len(root_url) is 0:
    app_url = ''
else:
    app_url = root_url + '/'

urlpatterns = [
    url(r'^' + app_url + 'api/auth/', include('rest_framework.urls')),
    url(r'^' + app_url + 'api/movies/$', movie_views.MovieList.as_view()),
    url(r'^' + app_url + 'api/movies/(?P<pk>[0-9]+)/$', movie_views.MovieDetail.as_view()),
    url(r'^' + app_url + 'api/settings/(?P<singleton_enforce>[0-9]+)/$', config_views.ConfigList.as_view()),
    url(r'^' + app_url + 'api/login/', ObtainJSONWebToken.as_view(serializer_class=CustomJWTSerializer)),
    url(r'^' + app_url + 'api/refresh/', refresh_jwt_token),
    url(r'^' + app_url + 'admin/', admin.site.urls),
]
