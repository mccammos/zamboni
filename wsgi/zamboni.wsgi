import os
import site

import django.core.handlers.wsgi


# Add the parent dir of zamboni to the python path so we can import manage
# (which sets other path stuff) and settings.
wsgidir = os.path.dirname(__file__)
site.addsitedir(os.path.abspath(os.path.join(wsgidir, '../../')))

# zamboni.manage adds the `apps` and `lib` directories to the path.
import zamboni.manage

os.environ['DJANGO_SETTINGS_MODULE'] = 'zamboni.local_settings'

# This is what mod_wsgi runs.
application = django.core.handlers.wsgi.WSGIHandler()

# Uncomment this to figure out what's going on with the mod_wsgi environment.
# def application(env, start_response):
#     start_response('200 OK', [('Content-Type', 'text/plain')])
#     return '\n'.join('%s: %s' % item for item in sorted(env.items()))
