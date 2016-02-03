import requests
import logging

from requests.packages.urllib3 import Timeout

from config.models import Config

logger = logging.getLogger(__name__)


def add(imdb):
    conf = Config.objects.get()
    couch_potato_url = '{host}:{port}{dir}/api/{api}/movie.add?identifier={imdb}'.format(host=conf.couchpotato_host,
                                                                                         port=conf.couchpotato_port,
                                                                                         dir=conf.couchpotato_directory,
                                                                                         api=conf.couchpotato_api,
                                                                                         imdb=imdb)

    try:
        request = requests.get(couch_potato_url, timeout=5)

        if request.json()['success']:
            return True
        else:
            return False

    except requests.RequestException as error:
        logger.error(error)
        logger.warn('Error connecting to CouchPotato')
        return None
