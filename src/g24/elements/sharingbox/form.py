from Acquisition import aq_inner, aq_base
from Acquisition.interfaces import IAcquirer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.event.base import (
    default_timezone,
    default_end_dt,
    default_start_dt
)
from plone.app.textfield.value import RichTextValue
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
from g24.elements.interfaces import IBasetypeAccessor
from g24.elements import messageFactory as _


EDIT, ADD = 0, 1

G24_BASETYPE = 'g24.elements.basetype'
FEATURES = [
    'is_thread',
    'is_event',
    'is_place'
]
DEFAULTS = {
    'features-base': {
        'title': UNSET,
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
IGNORES = ['save', 'cancel']

def create(context, type_):
    """ Create element, set attributes and add it to container.

    """

    fti = getUtility(IDexterityFTI, name=type_)

    container = aq_inner(context)
    obj = createObject(fti.factory)

    # Note: The factory may have done this already, but we want to be sure
    # that the created type has the right portal type. It is possible
    # to re-define a type through the web that uses the factory from an
    # existing type, but wants a unique portal_type!

    if hasattr(obj, '_setPortalTypeName'):
        obj._setPortalTypeName(fti.getId())

    # Acquisition wrap temporarily to satisfy things like vocabularies
    # depending on tools
    if IAcquirer.providedBy(obj):
        obj = obj.__of__(container)

    obj = aq_base(obj)
    if obj:
        notify(ObjectCreatedEvent(obj))
    return obj


def add(obj, container):
    # add
    container = aq_inner(container)
    obj = addContentToContainer(container, obj)
    if obj:
        notify(ObjectAddedEvent(obj))
    return obj


def edit(obj, data, order=None, ignores=None):
    """ Edit the attributes of an object.

        @param data:    Flat data structure:   {fieldname: value}

        @param order:   Optional list of attribute names to be set in the
                        defined order. If a attribute defined in order isn't
                        found in data, it is deleted from the object.

        @param ignores: Optional list of attribute names to be ignored.

    """

    # access content via an accessor, respecting the behaviors
    accessor = IBasetypeAccessor(obj)

    # first set attributes in the order as defined in order
    for attr in order:
        if attr in data:
            setattr(accessor, attr, data[attr])
        elif hasattr(accessor, attr): # attr not in data
            delattr(accessor, attr)

    # then set all other
    for key, val in data.iteritems():
        if key in order or key in ignores: continue
        setattr(accessor, key, val)

    obj.reindexObject()


def _flatten_data(data):
    """ Flatten the nested data structure.

        @param data: Nested data structure: {fieldset: {fieldname: value}}

        @param feature_fieldset_map: Dictionary with featurename to fieldsets
        @param required_or_delete: List of fieldnames which are required or -
                                   if the value is not present in data, deleted
                                   from the object.

        @returns:    Flat data structure:   {fieldname: value}

        The fieldnames should be unique over the data parameter nested
        structure. Two keys with the same name are getting overwritten.

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
        self.defaults['features-event']['start'] = default_start_dt()
        self.defaults['features-event']['end'] = default_end_dt()
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
        flat_data = _flatten_data(data.extracted)
        obj = self._save(flat_data)
        # return the rendered element html snippet
        self.request.response.redirect('%s%s' % (obj.absolute_url(), '/element'))

    def _save(self, data):
        raise NotImplementedError

    #    def set_data(self, obj, data):
    #
    #        # access content via an accessor, respecting the behaviors
    #        accessor = IBasetypeAccessor(obj)
    #
    #        # first, en/disable behaviors
    #        for feature in self.features:
    #            setattr(accessor, feature, data['features'][feature].extracted)
    #
    #        # then set all other attributes
    #        for basepath, keys in self.defaults.items():
    #            for key in keys:
    #                datum = data[basepath][key].extracted
    #                if basepath == 'features-title' and not data['features']['is_title'].extracted or\
    #                   basepath == 'features-event' and not data['features']['is_event'].extracted:
    #                    try: delattr(accessor, key)
    #                    except AttributeError: continue
    #                    continue
    #
    #                if datum is UNSET: continue
    #                else:
    #                    if key=='text': # TODO: yafowil should return unicode object here...
    #                        datum = RichTextValue(raw=unicode(datum.decode('utf-8')))
    #                    setattr(accessor, key, datum)
    #
    #        obj.reindexObject()


    # features

    @property
    def is_thread(self):
        # If posting has more than 2 children: True
        # If not: False
        if self.mode == ADD: return False # default
        else: return IBasetypeAccessor(self.context).is_thread

    @property
    def is_event(self):
        if self.mode == ADD: return False # default
        else: return IBasetypeAccessor(self.context).is_event

    @property
    def is_place(self):
        if self.mode == ADD: return False # default
        else: return IBasetypeAccessor(self.context).is_place


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

    def get(self, key, basepath):
        return self.defaults[basepath][key]


class SharingboxEdit(Sharingbox):
    mode = EDIT

    def _save(self, data):
        edit(self.context, data, order=self.features, ignores=self.ignores)
        #self.set_data(self.context, data)
        notify(ObjectModifiedEvent(self.context))
        IStatusMessage(self.request).addStatusMessage(_(u"Item edited"), "info")
        return self.context

    def get(self, key, basepath):
        accessor = IBasetypeAccessor(self.context)
        datum = getattr(accessor, key, None)
        if not datum: datum = self.defaults[basepath][key]
        if isinstance(datum, RichTextValue): # TODO: yafowil should return unicode object here...
            datum = datum.output
        return datum
