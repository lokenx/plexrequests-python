from django.conf.urls import url, include
from django.contrib import admin
from movies import views as movie_views
from config import views as config_views
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token


urlpatterns = [
    url(r'^api/auth/', include('rest_framework.urls')),
    url(r'^api/movies/$', movie_views.MovieList.as_view()),
    url(r'^api/movies/(?P<pk>[0-9]+)/$', movie_views.MovieDetail.as_view()),
    url(r'^api/settings/(?P<singleton_enforce>[0-9]+)/$', config_views.ConfigList.as_view()),
    url(r'^api/login/', obtain_jwt_token),
    url(r'^api/refresh/', refresh_jwt_token),
    url(r'^admin/', admin.site.urls),
]
