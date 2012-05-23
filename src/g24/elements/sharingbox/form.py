from Acquisition import aq_inner, aq_base
from Acquisition.interfaces import IAcquirer
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.event.base import default_timezone
from plone.app.textfield.value import RichTextValue
from plone.app.vocabularies.catalog import KeywordsVocabulary
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import addContentToContainer
from yafowil.base import UNSET
from yafowil.controller import Controller
from yafowil.yaml import parse_from_YAML
from zExceptions import Unauthorized
from zope.component import getUtility, createObject
from zope.event import notify
from zope.lifecycleevent import (
    ObjectAddedEvent,
    ObjectCreatedEvent,
    ObjectModifiedEvent
)
import pytz
from g24.elements.interfaces import IBasetypeAccessor
from g24.elements.behaviors import IPlace
from g24.elements import messageFactory as _


EDIT, ADD = 0, 1
FILEMARKER = object()

FEATURES = [
    'is_title',
    'is_event',
    'is_place'
]
DEFAULTS = {
    'features-title': { 'title': UNSET, },
    'features-base': {
        'text': UNSET,
        'subjects': UNSET
    },
    'features-event': {
        'start': UNSET,
        'end': UNSET,
        'timezone': UNSET,
        'whole_day': UNSET,
        'recurrence': UNSET,
        'location': UNSET,
    },
}


class Sharingbox(BrowserView):
    template = ViewPageTemplateFile('form.pt')
    mode = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.features = FEATURES
        self.defaults = DEFAULTS
        self.defaults['features-event']['timezone'] = default_timezone(self.context)
        self.defaults['features-base']['subjects'] = []

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
        self.request.response.redirect('%s%s' % (obj.absolute_url(), '/element'))

    def _save(self, data):
        raise NotImplementedError

    def set_data(self, obj, data):

        # access content via an accessor, respecting the behaviors
        accessor = IBasetypeAccessor(obj)

        # first, en/disable behaviors
        for feature in self.features:
            setattr(accessor, feature, data['features'][feature].extracted)

        # then set all other attributes
        for basepath, keys in self.defaults.items():
            for key in keys:
                datum = data[basepath][key].extracted
                if basepath == 'features-title' and not data['features']['is_title'].extracted or\
                   basepath == 'features-event' and not data['features']['is_event'].extracted:
                    try: delattr(accessor, key)
                    except AttributeError: continue
                    continue

                if datum is UNSET: continue
                else:
                    if key=='text': # TODO: yafowil should return unicode object here...
                        datum = RichTextValue(raw=unicode(datum.decode('utf-8')))
                    setattr(accessor, key, datum)

        obj.reindexObject()


    @property
    def is_title(self):
        # If posting has more than 2 children: True
        # If not: False
        if self.mode == ADD: return False # default
        else: return IBasetypeAccessor(self.context).is_title

    @property
    def is_event(self):
        if self.mode == ADD: return False # default
        else: return IBasetypeAccessor(self.context).is_event

    @property
    def is_place(self):
        if self.mode == ADD: return False # default
        else: return IBasetypeAccessor(self.context).is_place

    @property
    def vocabulary_timezones(self):
        return pytz.all_timezones

    @property
    def vocabulary_locations(self):
        cat = getToolByName(self.context, 'portal_catalog')
        query = {}
        query['object_provides'] = IPlace.__identifier__
        query['sort_on'] = 'sortable_title'
        return [it.Title for it in cat(**query)]

    @property
    def vocabulary_keywords(self):
        vocab = KeywordsVocabulary()
        result = vocab(self.context)
        return [(it.value, it.title) for it in result]



class SharingboxAdd(Sharingbox):
    portal_type = 'g24.elements.basetype'
    mode = ADD
    _finishedAdd = False

    def _save(self, data):
        obj = self.create()
        notify(ObjectCreatedEvent(obj))
        self.set_data(obj, data)
        obj = self.add(obj)
        if obj is not None:
            # mark only as finished if we get the new object
            notify(ObjectAddedEvent(obj))
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

    def get(self, key, basepath):
        return self.defaults[basepath][key]


class SharingboxEdit(Sharingbox):
    mode = EDIT

    def _save(self, data):
        self.set_data(self.context, data)
        notify(ObjectModifiedEvent(self.context))
        IStatusMessage(self.request).addStatusMessage(_(u"Item edited"), "info")
        return self.context

    def get(self, key, basepath):
        accessor = IBasetypeAccessor(self.context)
        datum = getattr(accessor, key, self.defaults[basepath][key])
        if isinstance(datum, RichTextValue): # TODO: yafowil should return unicode object here...
            datum = datum.output
        return datum
