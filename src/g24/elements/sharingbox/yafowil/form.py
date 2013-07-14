#from js.leaflet import leaflet
#from plone.fanstatic import groups
#groups.append(leaflet)
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from g24.elements import messageFactory as _
from g24.elements.browser.vocabularies import keywords, timezones, locations
from g24.elements.interfaces import IBasetypeAccessor
from g24.elements.sharingbox.crud import add
from g24.elements.sharingbox.crud import create
from g24.elements.sharingbox.crud import edit
from plone.app.event.base import default_end
from plone.app.event.base import default_start
from plone.app.event.base import default_timezone
from plone.app.textfield.value import RichTextValue
from yafowil.base import UNSET
from yafowil.controller import Controller
from yafowil.yaml import parse_from_YAML
from zExceptions import Unauthorized
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


EDIT, ADD = 0, 1
G24_BASETYPE = 'g24.elements.basetype'
FEATURES = [
    'is_thread',
    'is_event',
    'is_place'
]
DEFAULTS = {
    # FEATURES
    'is_thread': False,
    'is_event': False,
    'is_place': False,
    # BASE
    'title': UNSET,
    'text': UNSET,
    'subjects': UNSET,
    # EVENT
    'start': UNSET,
    'end': UNSET,
    'timezone': UNSET,
    'whole_day': UNSET,
    'recurrence': UNSET,
    'location': UNSET,
    'altitude': UNSET,
    'latitude': UNSET,
    'longitude': UNSET,
}
IGNORES = ['save', 'cancel']


def _flatten_data(data):
    """Flatten the nested data structure.

    :param data: Nested data structure: {fieldset: {fieldname: value}}
    :type data: dict

    :returns: Flat data structure: {fieldname: value}
    :rtype: dict

    The fieldnames should be unique over the data parameter nested structure.
    Two keys with the same name are getting overwritten.
    """
    items = {}
    for key, val in data.iteritems():
        if isinstance(val, dict):
            items.update(_flatten_data(val))
        else:
            items[key] = val
    return items


class Sharingbox(BrowserView):
    template = ViewPageTemplateFile('form.pt')
    mode = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.ignores = IGNORES
        self.features = FEATURES
        self.defaults = DEFAULTS
        self.defaults['start'] = default_start()
        self.defaults['end'] = default_end()
        self.defaults['timezone'] = default_timezone(self.context)
        self.defaults['subjects'] = []

    def _fetch_form(self):
        return parse_from_YAML('g24.elements.sharingbox:form.yaml', self, _)

    def __call__(self):
        form = self._fetch_form()
        self.controller = Controller(form, self.request)
        if not self.controller.next:
            return self.template()
        if "location" not in self.request.RESPONSE.headers:
            self.request.RESPONSE.redirect(self.controller.next)

    def next(self, request):
        return self.context.absolute_url()

    @property
    def action(self):
        postfix = self.mode == ADD and 'add' or 'edit'
        url = self.context.absolute_url()
        return '%s/@@sharingbox_%s' % (url, postfix)

    def save(self, widget, data):
        if self.request.method != 'POST':
            raise Unauthorized('POST only')
        obj = self._save(data.extracted)
        # return the rendered element html snippet
        self.request.response.redirect('%s%s' % (obj.absolute_url(), '/element'))

    def _save(self, data):
        raise NotImplementedError

    @property
    def vocabulary_keywords(self):
        return keywords(self.context)

    @property
    def vocabulary_timezones(self):
        return timezones()

    @property
    def vocabulary_locations(self):
        return locations(self.context)


class SharingboxAdd(Sharingbox):
    portal_type = G24_BASETYPE
    mode = ADD

    def _save(self, data):
        obj = create(self.context, self.portal_type)
        edit(obj, data, order=self.features, ignores=self.ignores)
        obj = add(obj, self.context)
        if obj:
            IStatusMessage(self.request).addStatusMessage(_(u"Item created"), "info")
        return obj

    def get(self, key):
        return self.defaults[key]


class SharingboxEdit(Sharingbox):
    mode = EDIT

    def _save(self, data):
        edit(self.context, data, order=self.features, ignores=self.ignores)
        #self.set_data(self.context, data)
        notify(ObjectModifiedEvent(self.context))
        IStatusMessage(self.request).addStatusMessage(_(u"Item edited"), "info")
        return self.context

    def get(self, key):
        accessor = IBasetypeAccessor(self.context)
        attr = getattr(accessor, key, None)
        if not attr:
            attr = self.defaults[key]
        if isinstance(attr, RichTextValue): # TODO: yafowil should return unicode object here...
            attr = attr.output
        return attr
