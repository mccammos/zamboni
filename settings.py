# -*- coding: utf-8 -*-
# Django settings for zamboni project.

import os
import logging
import socket

import product_details

# Make filepaths relative to settings.
ROOT = os.path.dirname(os.path.abspath(__file__))
path = lambda *a: os.path.join(ROOT, *a)

# We need to track this because hudson can't just call its checkout "zamboni".
# It puts it in a dir called "workspace".  Way to be, hudson.
ROOT_PACKAGE = os.path.basename(ROOT)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_PROPAGATE_EXCEPTIONS = True
LOG_LEVEL = logging.DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'NAME': 'zamboni',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '',
        'PORT': '',
        'USER': '',
        'PASSWORD': '',
        'OPTIONS': {'init_command': 'SET storage_engine=InnoDB'},
        'TEST_CHARSET': 'utf8',
        'TEST_COLLATION': 'utf8_general_ci',
    },
}

DATABASE_ROUTERS = ('multidb.MasterSlaveRouter',)

# Put the aliases for your slave databases in this list.
SLAVE_DATABASES = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-US'

# Accepted locales
AMO_LANGUAGES = (
    'ar', 'ca', 'cs', 'da', 'de', 'el', 'en-US', 'es-ES', 'eu',
    'fa', 'fi', 'fr', 'ga-IE', 'he', 'hu', 'id', 'it', 'ja', 'ko',
    'mn', 'nl', 'pl', 'pt-BR', 'pt-PT', 'ro', 'ru', 'sk', 'sq',
    'sv-SE', 'uk', 'vi', 'zh-CN', 'zh-TW',
)

# Override Django's built-in with our native names
LANGUAGES = dict([(i.lower(), product_details.languages[i]['native'])
                 for i in AMO_LANGUAGES])
RTL_LANGUAGES = ('ar', 'fa', 'fa-IR', 'he')

LANGUAGE_URL_MAP = dict([(i.lower(), i) for i in AMO_LANGUAGES])

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# The host currently running the site.  Only use this in code for good reason;
# the site is designed to run on a cluster and should continue to support that
HOSTNAME = socket.gethostname()

# Full base URL for your main site including protocol.  No trailing slash.
#   Example: https://addons.mozilla.org
SITE_URL = 'http://%s' % HOSTNAME

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media//'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# paths that don't require an app prefix
SUPPORTED_NONAPPS = ('admin', 'developers', 'editors', 'img', 'jsi18n',
                     'localizers', 'media', 'statistics', 'services')
DEFAULT_APP = 'firefox'

# paths that don't require a locale prefix
SUPPORTED_NONLOCALES = ('img', 'media', 'services',)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'r#%9w^o_80)7f%!_ir5zx$tu3mupw9u%&s!)-_q%gy7i+fhx#)'

# Templates

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.csrf',

    'django.contrib.messages.context_processors.messages',

    'amo.context_processors.app',
    'amo.context_processors.i18n',
    'amo.context_processors.global_settings',
)

TEMPLATE_DIRS = (
    path('templates'),
)

def JINJA_CONFIG():
    import jinja2
    from django.conf import settings
    from caching.base import cache
    config = {'extensions': ['l10n.template.i18n', 'caching.ext.cache',
                             'jinja2.ext.with_', 'jinja2.ext.loopcontrols'],
              'finalize': lambda x: x if x is not None else ''}
    if 'memcached' in cache.scheme and not settings.DEBUG:
        # We're passing the _cache object directly to jinja because
        # Django can't store binary directly; it enforces unicode on it.
        # Details: http://jinja.pocoo.org/2/documentation/api#bytecode-cache
        # and in the errors you get when you try it the other way.
        bc = jinja2.MemcachedBytecodeCache(cache._cache,
                                           "%sj2:" % settings.CACHE_PREFIX)
        config['cache_size'] = -1  # Never clear the cache
        config['bytecode_cache'] = bc
    return config



MIDDLEWARE_CLASSES = (
    # AMO URL middleware comes first so everyone else sees nice URLs.
    'amo.middleware.LocaleAndAppURLMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'cake.middleware.CakeCookieMiddleware',
    # This should come after authentication middle ware
    'access.middleware.ACLMiddleware',
)

# Auth
AUTHENTICATION_BACKENDS = (
    'users.backends.AmoUserBackend',
    'cake.backends.SessionBackend',
)
AUTH_PROFILE_MODULE = 'users.UserProfile'

ROOT_URLCONF = '%s.urls' % ROOT_PACKAGE

INSTALLED_APPS = (
    'amo',
    'access',
    'addons',
    'admin',
    'api',
    'applications',
    'bandwagon',
    'blocklist',
    'browse',
    'cronjobs',
    'devhub',
    'editors',
    'files',
    'l10n',  # for ./manage.py extract
    'minify',
    'nick',
    'reviews',
    'search',
    'sharing',
    'stats',
    'tags',
    'translations',
    'users',
    'versions',

    # We need this so the jsi18n view will pick up our locale directory.
    ROOT_PACKAGE,

    'cake',
    'django_nose',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
)

# These apps will be removed from INSTALLED_APPS in a production environment.
DEV_APPS = (
    'django_nose',
)

# Tests
TEST_RUNNER = 'test_utils.runner.RadicalTestSuiteRunner'

# If you want to run Selenium tests, you'll need to have a server running.
# Then give this a dictionary of settings.  Something like:
#    'HOST': 'localhost',
#    'PORT': 4444,
#    'BROWSER': '*firefox', # Alternative: *safari
SELENIUM_CONFIG = {}

# Tells the extract script what files to look for l10n in and what function
# handles the extraction.  The Tower library expects this.
DOMAIN_METHODS = {
    'messages': [
        ('apps/**.py',
            'l10n.management.commands.extract.extract_amo_python'),
        ('**/templates/**.html',
            'l10n.management.commands.extract.extract_amo_template'),
    ],
    'lhtml': [
        ('**/templates/**.lhtml',
            'l10n.management.commands.extract.extract_amo_template'),
    ],
    'javascript': [
        # We can't say **.js because that would dive into mochikit and timeplot
        # and all the other baggage we're carrying.  Timeplot, in particular,
        # crashes the extractor with bad unicode data.
        ('media/js/*.js', 'javascript'),
        ('media/js/amo2009/**.js', 'javascript'),
        ('media/js/zamboni/**.js', 'javascript'),
    ],
}

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        # CSS files common to the entire site.
        'common': (
            'css/main.css',
            'css/main-mozilla.css',
            'css/zamboni/zamboni.css',

            'css/jquery-lightbox.css',
            'css/autocomplete.css',
        ),
    },
    'js': {
        # JS files common to the entire site.
        'common': (
            'js/jquery-compressed.js',
            'js/zamboni/underscore-min.js',
            'js/amo2009/addons.js',
            'js/zamboni/init.js',
            'js/zamboni/buttons.js',
            'js/zamboni/search.js',

            'js/jquery.cookie.js',
            'js/amo2009/global.js',
            'js/amo2009/slimbox2.js',
            'js/jquery-ui/jqModal.js',
            'js/amo2009/home.js',
            'js/__utm.js',

            # add-ons details page
            'js/jquery-ui/ui.lightbox.js',
            'js/jquery.autocomplete.pack.js',
            'js/tags.js',
            'js/get-satisfaction-v2.js',
            'js/zamboni/contributions.js',
            'js/zamboni/addon_details.js',
        ),
    }
}


# Caching
# Prefix for cache keys (will prevent collisions when running parallel copies)
CACHE_PREFIX = 'amo:'

# Number of seconds a count() query should be cached.  Keep it short because
# it's not possible to invalidate these queries.
CACHE_COUNT_TIMEOUT = 60

# External tools.
SPHINX_INDEXER = 'indexer'
SPHINX_SEARCHD = 'searchd'
SPHINX_CONFIG_PATH = path('configs/sphinx/sphinx.conf')
SPHINX_HOST = '127.0.0.1'
SPHINX_PORT = 3312

JAVA_BIN = '/usr/bin/java'

# URL paths
# paths for images, e.g. mozcdn.com/amo or '/static'
STATIC_URL = SITE_URL
ADDON_ICON_URL = "%s/%s/%s/images/addon_icon/%%d/%%s" % (
        STATIC_URL, LANGUAGE_CODE, DEFAULT_APP)
PREVIEW_THUMBNAIL_URL = (STATIC_URL +
        '/img/uploads/previews/thumbs/%s/%d.png?modified=%d')
PREVIEW_FULL_URL = (STATIC_URL +
        '/img/uploads/previews/full/%s/%d.png?modified=%d')
USER_PIC_URL = STATIC_URL + '/img/uploads/userpics/%s/%s/%s.jpg?modified=%d'
# paths for uploaded extensions
FILES_URL = STATIC_URL + "/downloads/file/%d/%s?src=%s"
COLLECTION_ICON_URL = ('%s/%s/%s/images/collection_icon/%%s/%%s' %
                       (STATIC_URL, LANGUAGE_CODE, DEFAULT_APP))

# Outgoing URL bouncer
REDIRECT_URL = 'https://outgoing.mozilla.org/v1/'
REDIRECT_SECRET_KEY = ''

# Legacy Settings
# used by old-style CSRF token
CAKE_SESSION_TIMEOUT = 8640

# PayPal Settings
PAYPAL_CGI_URL = 'https://www.paypal.com/cgi-bin/webscr'

# Email settings
EMAIL_FROM_DEFAULT = 'nobody@mozilla.org'

# Please use all lowercase for the blacklist.
EMAIL_BLACKLIST = (
    'nobody@mozilla.org',
)
