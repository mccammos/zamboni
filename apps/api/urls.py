from django.conf.urls.defaults import patterns, url, include

from . import views


# Wrap class views in a lambda call so we get an instance of the class for view
# so we can be thread-safe.  Yes, this lambda function returns a lambda
# function.
class_view = lambda x: lambda *args, **kwargs: x()(*args, **kwargs)

# Regular expressions that we use in our urls.
type_regexp = '/(?P<addon_type>[^/]*)'
limit_regexp = '/(?P<limit>\d*)'
platform_regexp = '/(?P<platform>\w*)'
version_regexp = '/(?P<version>[^/]*)'


def build_urls(base, appendages):
    """
    Many of our urls build off each other:
    e.g.
    /search/:query
    /search/:query/:type
    .
    .
    /search/:query/:type/:limit/:platform/:version
    """
    urls = [base]
    for i in range(len(appendages)):
        urls.append(base+''.join(appendages[:i+1]))

    return urls


base_search_regexp = r'search/(?P<query>[^/]+)'
appendages = [type_regexp, limit_regexp, platform_regexp, version_regexp]
search_regexps = build_urls(base_search_regexp, appendages)

base_list_regexp = r'list'
appendages.insert(0, '/(?P<list_type>[^/]+)')
list_regexps = build_urls(base_list_regexp, appendages)


api_patterns = patterns('',
    # Addon_details
    url('addon/(?P<addon_id>\d+)$',
        class_view(views.AddonDetailView),
        name='api.addon_detail'),)

for regexp in search_regexps:
    api_patterns += patterns('',
        url(regexp + '/?$', class_view(views.SearchView), name='api.search'))

for regexp in list_regexps:
    api_patterns += patterns('',
            url(regexp + '/?$', class_view(views.ListView), name='api.list'))

urlpatterns = patterns('',
    # Redirect api requests without versions
    url('^((?:addon|search|list)/.*)$', views.redirect_view),

    # Append api_version to the real api views
    url(r'^(?P<api_version>\d+|\d+.\d+)/', include(api_patterns)),

)
