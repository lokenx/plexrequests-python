import os
import logging
import signals
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi

from django.core.wsgi import get_wsgi_application
from tornado.options import options, define, parse_command_line

define('port', type=int, default=8000)
define('root', type=str, default=' ')


def main():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'plexrequests.settings'

    parse_command_line()

    wsgi_app = get_wsgi_application()
    container = tornado.wsgi.WSGIContainer(wsgi_app)

    STATIC_PATH = os.getcwd() + "/static/"

    root_url_file = open('plexrequests/root_url.txt', 'w+')

    if len(options.root) is 1:
        root = ''
    else:
        root = options.root

    root_url_file.write(root)
    root_url_file.close()

    tornado_app = tornado.web.Application(
        [
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': STATIC_PATH}),
            (r'.*', tornado.web.FallbackHandler, dict(fallback=container)),
        ])

    os.system('python manage.py collectstatic -v 0 --clear --noinput')

    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port)

    logger = logging.getLogger(__name__)
    logger.info('Server started at http://localhost:{}/{}'.format(options.port, options.root))

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        logger.info('Server stopped')


if __name__ == '__main__':
    main()
