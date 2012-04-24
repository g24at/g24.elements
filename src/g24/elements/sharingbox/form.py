from zope.event import notify
from zope.i18nmessageid import MessageFactory
from zExceptions import Unauthorized
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import yafowil.loader
from yafowil.base import UNSET
from yafowil.controller import Controller
from yafowil.yaml import parse_from_YAML
"""
from g24.elements.interfaces import IBasetype
from g24.elements.events import (
    ElementCreatedEvent,
    ElementModifiedEvent
)
"""
_ = MessageFactory('g24.elements')


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
        self.request.RESPONSE.redirect(self.controller.next)

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
    mode = ADD

class SharingboxEdit(Sharingbox):
    mode = EDIT
