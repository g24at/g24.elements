from Acquisition import aq_inner, aq_base
from Acquisition.interfaces import IAcquirer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.textfield.value import RichTextValue
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import addContentToContainer
from yafowil.base import UNSET
from yafowil.controller import Controller
from yafowil.yaml import parse_from_YAML
from zExceptions import Unauthorized
from zope.component import getUtility, createObject
from zope.event import notify

from g24.elements.instancebehaviors import enable_behaviors, disable_behaviors
from g24.elements.config import EVENT_INTERFACES, EVENT_BEHAVIORS
from g24.elements import messageFactory as _


"""
from g24.elements.events import (
    ElementCreatedEvent,
    ElementModifiedEvent
)
"""


EDIT, ADD = 1, 2
FILEMARKER = object()
THREAD_DEFAULTS = {
    'title': UNSET,
}
TEXT_DEFAULTS = {
    'text': UNSET,
}
EVENT_DEFAULTS = {
    'start': UNSET,
    'end': UNSET,
    'whole_day': UNSET,
    'recurrence': UNSET,
}
LOCATION_DEFAULTS = {
    'location': UNSET,
}
ORGANIZER_DEFAULTS = {
    'organizer': UNSET,
}
DEFAULTS = dict(
    THREAD_DEFAULTS.items() +
    TEXT_DEFAULTS.items() +
    EVENT_DEFAULTS.items() +
    LOCATION_DEFAULTS.items() +
    ORGANIZER_DEFAULTS.items()
)

class Sharingbox(BrowserView):
    template = ViewPageTemplateFile('form.pt')
    mode = None

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
        obj = self._save(data)
        self.request.response.redirect(obj.absolute_url())

    def _safe(self, data):
        raise NotImplementedError

    def set_data(self, obj, data):

        # fist, en/disable behaviors
        if data['is_event'].extracted:
            enable_behaviors(obj, EVENT_BEHAVIORS, EVENT_INTERFACES)
        else:
            disable_behaviors(obj, EVENT_BEHAVIORS, EVENT_INTERFACES)

        # then set all the attributes
        for key in DEFAULTS:
            datum = data[key].extracted
            if datum is UNSET: continue
            else:
                if key=='text': # TODO: yafowil should return unicode object here...
                    datum = RichTextValue(raw=unicode(datum.encode('utf-8')))

                if key in THREAD_DEFAULTS:
                    if not data['is_thread'].extracted:
                        try: delattr(obj, key)
                        except AttributeError: continue
                        continue

                if key in EVENT_DEFAULTS:
                    if not data['is_event'].extracted:
                        try: delattr(obj, key)
                        except AttributeError: continue
                        continue

                if key in LOCATION_DEFAULTS:
                    if not data['is_location'].extracted:
                        try: delattr(obj, key)
                        except AttributeError: continue
                        continue

                if key in ORGANIZER_DEFAULTS:
                    if not data['is_organizer'].extracted:
                        try: delattr(obj, key)
                        except AttributeError: continue
                        continue

                setattr(obj, key, datum)


    @property
    def is_thread(self):
        if self.mode == ADD: return True # default
        else: return bool(self.context.title)

    @property
    def is_event(self):
        if self.mode == ADD: return False # default
        else: return IDXEvent.providedBy(self.context)

    @property
    def is_location(self):
        return False

    @property
    def is_organizer(self):
        return False


class SharingboxAdd(Sharingbox):
    portal_type = 'g24.elements.basetype'
    mode = ADD
    _finishedAdd = False

    def _save(self, data):
        obj = self.create()
        self.set_data(obj, data)
        obj = self.add(obj)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True
            IStatusMessage(self.request).addStatusMessage(_(u"Item created"), "info")
        return obj

    def create(self):
        fti = getUtility(IDexterityFTI, name=self.portal_type)

        container = aq_inner(self.context)
        content = createObject(fti.factory)

        # Note: The factory may have done this already, but we want to be sure
        # that the created type has the right portal type. It is possible
        # to re-define a type through the web that uses the factory from an
        # existing type, but wants a unique portal_type!

        if hasattr(content, '_setPortalTypeName'):
            content._setPortalTypeName(fti.getId())

        # Acquisition wrap temporarily to satisfy things like vocabularies
        # depending on tools
        if IAcquirer.providedBy(content):
            content = content.__of__(container)

        return aq_base(content)

    def add(self, object):
        container = aq_inner(self.context)
        return addContentToContainer(container, object)

    def get(self, key):
        return DEFAULTS[key]


class SharingboxEdit(Sharingbox):
    mode = EDIT

    def _save(self, data):
        self.set_data(self.context, data)
        IStatusMessage(self.request).addStatusMessage(_(u"Item edited"), "info")
        return self.context

    def get(self, key):
        datum = getattr(self.context, key, DEFAULTS[key])
        if isinstance(datum, RichTextValue): # TODO: yafowil should return unicode object here...
            datum = datum.output
        return datum
