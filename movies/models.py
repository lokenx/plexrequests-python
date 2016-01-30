from django.db import models


class Movie(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    year = models.IntegerField(default=0)
    imdb = models.CharField(max_length=100, unique=True)
    downloaded = models.BooleanField(default=False)
    poster_path = models.CharField(max_length=100, blank=True, default='')
    approved = models.BooleanField(default=False)
    pending = models.BooleanField(default=True)
    requested_by = models.ForeignKey('auth.User', related_name='movies')

    class Meta:
        ordering = ('created',)
