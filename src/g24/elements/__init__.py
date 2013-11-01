# -*- coding: utf-8 -*-
from zope.i18nmessageid import MessageFactory
packageName = __name__
messageFactory = MessageFactory(packageName)


def safe_decode(value, encoding='utf-8'):
    """Converts a value to unicode, even it is already a unicode string.
    from Products.CMFPlone.utils.safe_unicode

    >>> from g24.elements import safe_decode
    >>> safe_decode('bla')
    u'bla'
    >>> safe_decode(u'uhh')
    u'uhh'
    >>> safe_decode(123)
    123

    """
    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        try:
            value = unicode(value, encoding)
        except (UnicodeDecodeError):
            value = value.decode('utf-8', 'replace')
    return value


def safe_encode(value):
    """ Return utf-8 encoded string if value is a unicode.
    Otherwise, just return the value.

    >>> from g24.elements import safe_encode
    >>> safe_encode('bla')
    'bla'
    >>> safe_encode(u'uhh')
    'uhh'
    >>> safe_encode(123)
    123

    """
    if isinstance(value, unicode):
        return value.encode('utf-8')
    else:
        return value

from plone.app.widgets.browser import vocabulary
orig_permissions = vocabulary._permissions
vocabulary._permissions.update({
    'g24.elements.Locations': 'Modify portal content',
    'plone.app.event.Timezones': 'Modify portal content',
    'plone.app.event.AvailableTimezones': 'Modify portal content',
    'collective.address.CountryVocabulary': 'Modify portal content'
})


from collective.address.behaviors import IAddress
from collective.geolocationbehavior.geolocation import IGeolocatable
from plone.formwidget.geolocation.geolocation import Geolocation
from z3c.form.widget import ComputedWidgetAttribute
from zope.component import provideAdapter


# DEFAULT COUNTRY for IAddress behaviors in collective.venue
DEFAULT_COUNTRY = "040"  # Austria
provideAdapter(ComputedWidgetAttribute(
    lambda data: DEFAULT_COUNTRY,
    field=IAddress['country']), name='default')


def default_city(data):
    ret = u'Graz'
    return ret
provideAdapter(ComputedWidgetAttribute(
    default_city,
    field=IAddress['city']), name='default')


def default_zip_code(data):
    ret = u'8010'
    return ret
provideAdapter(ComputedWidgetAttribute(
    default_zip_code,
    field=IAddress['zip_code']), name='default')


def default_geo(data):
    ret = Geolocation(47.070714, 15.439503999999943)
    return ret
provideAdapter(ComputedWidgetAttribute(
    default_geo, field=IGeolocatable['geolocation']), name='default')
