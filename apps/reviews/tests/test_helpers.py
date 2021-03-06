from nose.tools import eq_

import jingo
from pyquery import PyQuery

from addons.models import Addon


def setup():
    jingo.load_helpers()


def render(s, context={}):
    t = jingo.env.from_string(s)
    return t.render(**context)


def test_stars():
    s = render('{{ num|stars }}', {'num': None})
    eq_(s, 'Not yet rated')

    s = render('{{ num|stars }}', {'num': 1})
    msg = 'Rated 1 out of 5 stars'
    eq_(s, '<span class="stars stars-1" title="{0}">{0}</span>'.format(msg))


def test_reviews_link():
    a = Addon(average_rating=4, total_reviews=37, id=1)
    s = render('{{ myaddon|reviews_link }}', {'myaddon': a})
    eq_(PyQuery(s)('strong').text(), '37 reviews')

    # without collection uuid
    eq_(PyQuery(s)('a').attr('href'), '/en-US/firefox/addon/1/#reviews')

    # with collection uuid
    myuuid = 'f19a8822-1ee3-4145-9440-0a3640201fe6'
    s = render('{{ myaddon|reviews_link(myuuid) }}', {'myaddon': a,
                                                      'myuuid': myuuid})
    eq_(PyQuery(s)('a').attr('href'),
        '/en-US/firefox/addon/1/?collection_uuid=%s#reviews' % myuuid)
