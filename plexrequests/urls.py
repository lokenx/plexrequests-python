from django.conf.urls import url, include
from django.contrib import admin
from movies import views


urlpatterns = [
    url(r'^api/auth/', include('rest_framework.urls')),
    url(r'^api/movies/$', views.MovieList.as_view()),
    url(r'^api/movies/(?P<pk>[0-9]+)/$', views.MovieDetail.as_view()),
    url(r'^admin/', admin.site.urls),
]
