from decimal import Decimal

from django.core.cache import cache

from nose.tools import eq_
from test_utils import ExtraAppTestCase

from amo.fields import DecimalCharField

from fieldtestapp.models import DecimalCharFieldModel


class DecimalCharFieldTestCase(ExtraAppTestCase):
    fixtures = ['fieldtestapp/test_models.json']
    extra_apps = ['amo.tests.fieldtestapp']

    def setUp(self):
        cache.clear()

    def test_fetch(self):
        o = DecimalCharFieldModel.objects.get(id=1)

        eq_(o.strict, Decimal('1.23'))
        eq_(o.loose, None)
