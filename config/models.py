from django.db import models


class Config(models.Model):
    site_title = models.CharField(max_length=255, default='Plex Requests')
    site_tagline = models.CharField(max_length=255, default="Want to watch something but it's not currently on Plex? Select an option below and do a quick search!")

    search_movie = models.BooleanField(default=True)
    search_tv = models.BooleanField(default=True)
    search_music = models.BooleanField(default=True)

    limit_movie = models.IntegerField(default=0)
    limit_tv = models.IntegerField(default=0)
    limit_music = models.IntegerField(default=0)

    requests_approval = models.BooleanField(default=False)

    singleton_enforce = models.IntegerField(default = 1, unique = True)


    def save(self, *args, **kwargs):
        """
        Save object to the database. Removes all other entries if there
        are any.
        """
        self.__class__.objects.exclude(id=self.id).delete()
        super(Config, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Load object from the database. Failing that, create a new empty
        (default) instance of the object and return it (without saving it
        to the database).
        """

        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()