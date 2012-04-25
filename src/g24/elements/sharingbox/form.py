import copy
from Acquisition import aq_inner, aq_base
from Acquisition.interfaces import IAcquirer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import addContentToContainer
from yafowil.base import UNSET
from yafowil.controller import Controller
from yafowil.yaml import parse_from_YAML
from zExceptions import Unauthorized
from zope.component import getUtility, createObject
from zope.event import notify
from g24.elements.content import IBasetype
from g24.elements import messageFactory as _
"""
from g24.elements.events import (
    ElementCreatedEvent,
    ElementModifiedEvent
)
"""


EDIT, ADD = 1, 2
FILEMARKER = object()
DEFAULTS = {
    'is_thread': UNSET,
    'is_event': UNSET,
    'is_location': UNSET,
    'is_organizer': UNSET,
    'title': UNSET,
    'text': UNSET,
    'start': UNSET,
    'end': UNSET,
    'whole_day': UNSET,
    'recurrence': UNSET,
    'location': UNSET,
    'organizer': UNSET,
}

class Sharingbox(BrowserView):
    template = ViewPageTemplateFile('form.pt')
    mode = None

    def _fetch_form(self):
        return parse_from_YAML('g24.elements.sharingbox:form.yaml', self, _)

    def __call__(self):
        self.data = dict(DEFAULTS)
        if self.mode == EDIT and IBasetype.providedBy(self.context):
            self.mode = EDIT
            self.data = self.get_data(self.context)

        form = self._fetch_form()
        self.controller = Controller(form, self.request)
        if not self.controller.next:
            return self.template()
        if "location" not in self.request.RESPONSE.headers:
            self.request.RESPONSE.redirect(self.controller.next)

    def next(self, request):
        return self.context.absolute_url() + '/view'

    @property
    def action(self):
        postfix = self.mode == ADD and 'add' or 'edit'
        url = self.context.absolute_url()
        return '%s/@@sharingbox_%s' % (url, postfix)

    def save(self, widget, data):
        if self.request.method != 'POST':
            raise Unauthorized('POST only')
        self._save(data)

        self.request.RESPONSE.redirect(self.controller.next)

    def _safe(self, data):
        raise NotImplementedError

    def get_data(self, obj):
        for key in DEFAULTS:
            attr = getattr(key, obj, None)
            if attr: self.data.update(key, attr)

    def set_data(self, obj, data):
        for key in DEFAULTS:
            datum = data[key].extracted
            if datum is UNSET: continue
            else:
                attr = getattr(key, obj, None)
                if attr: attr = datum

    @property
    def is_event(self):
        return False
        #return IEvent.providedBy(self.context)
        #return bool(self.context.data['start'])

    @property
    def is_thread(self):
        return False

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
        self.add(obj)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True
            IStatusMessage(self.request).addStatusMessage(_(u"Item created"), "info")

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

        fti = getUtility(IDexterityFTI, name=self.portal_type)
        container = aq_inner(self.context)
        new_object = addContentToContainer(container, object)

        if fti.immediate_view:
            self.immediate_view = "%s/%s/%s" % (container.absolute_url(), new_object.id, fti.immediate_view,)
        else:
            self.immediate_view = "%s/%s" % (container.absolute_url(), new_object.id)


class SharingboxEdit(Sharingbox):
    mode = EDIT

    def _save(self, data):
        self.set_data(self.context, data)
        IStatusMessage(self.request).addStatusMessage(_(u"Item edited"), "info")
