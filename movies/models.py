from django.db import models


class Movie(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    release_date = models.DateField(null=True)
    id = models.IntegerField(unique=True, primary_key=True)
    imdb = models.CharField(max_length=100, blank=True)
    downloaded = models.BooleanField(default=False)
    poster_path = models.CharField(max_length=100, blank=True, default='')
    approved = models.BooleanField(default=False)
    pending = models.BooleanField(default=True)
    requested_by = models.ForeignKey('auth.User', related_name='movies')

    class Meta:
        ordering = ('created',)
