from django.conf import settings

from nose.tools import eq_
import test_utils
from pyquery import PyQuery as pq

import amo
from amo.urlresolvers import reverse
from addons.models import Addon, AddonUser
from users.models import UserProfile


class TestHomepage(test_utils.TestCase):
    fixtures = ['base/addons', 'base/global-stats', 'base/featured']

    def setUp(self):
        super(TestHomepage, self).setUp()
        self.base_url = reverse('home')

    def test_default_feature(self):
        response = self.client.get(self.base_url, follow=True)
        eq_(response.status_code, 200)
        eq_(response.context['filter'].field, 'featured')

    def test_featured(self):
        response = self.client.get(self.base_url + '?browse=featured',
                                   follow=True)
        eq_(response.status_code, 200)
        eq_(response.context['filter'].field, 'featured')
        featured = response.context['addon_sets']['featured']
        ids = [a.id for a in featured]
        eq_(set(ids), set([2464, 7661]))
        for addon in featured:
            assert addon.is_featured(amo.FIREFOX, settings.LANGUAGE_CODE)

    def _test_invalid_feature(self):
        response = self.client.get(self.base_url + '?browse=xxx')
        self.assertRedirects(response, '/en-US/firefox/', status_code=301)

    def test_no_experimental(self):
        response = self.client.get(self.base_url)
        for addons in response.context['addon_sets'].values():
            for addon in addons:
                assert addon.status != amo.STATUS_SANDBOX

    def test_filter_opts(self):
        response = self.client.get(self.base_url)
        opts = [k[0] for k in response.context['filter'].opts]
        eq_(opts, 'featured popular new updated'.split())


class TestDetailPage(test_utils.TestCase):
    fixtures = ['base/addons', 'addons/listed']

    def tearDown(self):
        """Return URL prefixer to default."""
        prefixer = amo.urlresolvers.get_url_prefix()
        prefixer.app = settings.DEFAULT_APP

    def test_anonymous_user(self):
        """Does the page work for an anonymous user?"""
        response = self.client.get(reverse('addons.detail', args=[3615]),
                                   follow=True)
        eq_(response.status_code, 200)
        eq_(response.context['addon'].id, 3615)

    def test_inactive_addon(self):
        """Do not display disabled add-ons."""
        myaddon = Addon.objects.get(id=3615)
        myaddon.inactive = True
        myaddon.save()
        response = self.client.get(reverse('addons.detail', args=[myaddon.id]),
                                   follow=True)
        eq_(response.status_code, 404)

    def test_listed(self):
        """Show certain things for hosted but not listed add-ons."""
        hosted_resp = self.client.get(reverse('addons.detail', args=[3615]),
                                      follow=True)
        hosted = pq(hosted_resp.content)

        listed_resp = self.client.get(reverse('addons.detail', args=[3723]),
                                      follow=True)
        listed = pq(listed_resp.content)

        eq_(hosted('#releasenotes').length, 1)
        eq_(listed('#releasenotes').length, 0)

    def test_beta(self):
        """Test add-on with a beta channel."""
        my_addonid = 3615
        get_pq_content = lambda: pq(self.client.get(reverse(
            'addons.detail', args=[my_addonid]), follow=True).content)

        myaddon = Addon.objects.get(id=my_addonid)

        # Add a beta version and show it.
        mybetafile = myaddon.versions.all()[0].files.all()[0]
        mybetafile.status = amo.STATUS_BETA
        mybetafile.save()
        beta = get_pq_content()
        eq_(beta('#beta-channel').length, 1)

        # Now hide it.
        myaddon.show_beta = False
        myaddon.save()
        beta = get_pq_content()
        eq_(beta('#beta-channel').length, 0)

    def test_other_addons(self):
        """Test "other add-ons by author" list."""

        # Grab a user and give them some add-ons.
        u = UserProfile.objects.get(pk=2519)
        thisaddon = u.addons.all()[0]
        other_addons = Addon.objects.exclude(pk=thisaddon.pk)[:3]
        for addon in other_addons:
            AddonUser.objects.create(user=u, addon=addon)

        page = self.client.get(reverse('addons.detail', args=[thisaddon.id]),
                               follow=True)
        doc = pq(page.content)
        eq_(doc('.other-author-addons li').length, other_addons.count())
        for i in range(other_addons.count()):
            link = doc('.other-author-addons li a').eq(i)
            eq_(link.attr('href'), other_addons[i].get_url_path())

    def test_compatible_app_redirect(self):
        """
        For add-ons incompatible with the current app, redirect to one
        that's supported.
        """
        addon = Addon.objects.get(id=3615)
        comp_app = addon.compatible_apps.keys()[0]
        not_comp_app = [ a for a in amo.APP_USAGE if a not in
                         addon.compatible_apps.keys() ][0]

        # no SeaMonkey version => redirect
        prefixer = amo.urlresolvers.get_url_prefix()
        prefixer.app = not_comp_app.short
        response = self.client.get(reverse('addons.detail', args=[addon.id]),
                                   follow=False)
        eq_(response.status_code, 301)
        eq_(response['Location'].find(not_comp_app.short), -1)
        assert (response['Location'].find(comp_app.short) >= 0)

        # compatible app => 200
        prefixer = amo.urlresolvers.get_url_prefix()
        prefixer.app = comp_app.short
        response = self.client.get(reverse('addons.detail', args=[addon.id]),
                                   follow=False)
        eq_(response.status_code, 200)

    def test_external_urls(self):
        """Check that external URLs are properly escaped."""
        addon = Addon.objects.get(id=1843)
        response = self.client.get(reverse('addons.detail', args=[addon.id]),
                                   follow=True)
        doc = pq(response.content)
        eq_(doc('#addon-summary a[href^="%s"]' %
                settings.REDIRECT_URL).length, 1)
