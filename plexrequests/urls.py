from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from movies import views as movie_views
from app import views as app_views

router = DefaultRouter()
router.register(r'users', app_views.UserViewSet)

urlpatterns = [
    url(r'^api/auth/', include('rest_framework.urls')),
    url(r'^api/movies/$', movie_views.MovieList.as_view()),
    url(r'^api/movies/(?P<pk>[0-9]+)/$', movie_views.MovieDetail.as_view()),
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
]
