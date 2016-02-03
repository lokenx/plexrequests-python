import logging

from django.db import models


logger = logging.getLogger(__name__)


class Config(models.Model):
    site_title = models.CharField(max_length=255, default='Plex Requests')
    site_tagline = models.CharField(max_length=255,
                                    default="Want to watch something but it's not currently on Plex? Select an option below and do a quick search!")

    search_movie = models.BooleanField(default=True)
    search_tv = models.BooleanField(default=True)
    search_music = models.BooleanField(default=True)

    limit_movie = models.IntegerField(default=0)
    limit_tv = models.IntegerField(default=0)
    limit_music = models.IntegerField(default=0)

    requests_approval = models.BooleanField(default=False)

    auth_required = models.BooleanField(default=False)
    auth_plextoken = models.CharField(max_length=255, default='abcd1234')

    couchpotato_enabled = models.BooleanField(default=False)
    couchpotato_host = models.CharField(max_length=255, default='http://192.168.0.1')
    couchpotato_port = models.IntegerField(default=5050)
    couchpotato_api = models.CharField(max_length=255, default='abcd1234')
    couchpotato_directory = models.CharField(max_length=255, blank=True, default='')

    sickrage_enabled = models.BooleanField(default=False)
    sickrage_host = models.CharField(max_length=255, default='http://192.168.0.1')
    sickage_port = models.IntegerField(default=8081)
    sickrage_api = models.CharField(max_length=255, default='abcd1234')
    sickrage_directory = models.CharField(max_length=255, blank=True, default='')

    sonarr_enabled = models.BooleanField(default=False)
    sonarr_host = models.CharField(max_length=255, default='http://192.168.0.1')
    sonarr_port = models.IntegerField(default=8989)
    sonarr_api = models.CharField(max_length=255, default='abcd1234')
    sonarr_directory = models.CharField(max_length=255, blank=True, default='')
    sonarr_quality = models.IntegerField(default=1)
    sonarr_root = models.CharField(max_length=255, default='/path/to/root/tv/folder')
    sonarr_season_folders = models.BooleanField(default=True)

    pushbullet_enabled = models.BooleanField(default=False)
    pushbullet_api = models.CharField(max_length=255, default='abcd1234')

    pushover_enabled = models.BooleanField(default=False)
    pushover_api = models.CharField(max_length=255, default='abcd1234')
    pushover_user = models.CharField(max_length=255, default='abcd1234')

    singleton_enforce = models.IntegerField(default=1, unique=True)

    def save(self, *args, **kwargs):
        """
        Save object to the database. Removes all other entries if there
        are any.
        """
        logger.info('Updated settings')
        self.__class__.objects.exclude(id=self.id).delete()
        super(Config, self).save(*args, **kwargs)
