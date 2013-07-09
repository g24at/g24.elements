from Acquisition import aq_inner, aq_base
from Acquisition.interfaces import IAcquirer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from g24.elements import messageFactory as _
from g24.elements.browser.vocabularies import keywords, timezones, locations
from g24.elements.interfaces import IBasetypeAccessor
from plone.app.event.base import default_end
from plone.app.event.base import default_start
from plone.app.event.base import default_timezone
from plone.app.event.dx.behaviors import first_weekday_sun0
from plone.app.textfield.value import RichTextValue
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import addContentToContainer
from yafowil.base import UNSET
from yafowil.controller import Controller
from yafowil.yaml import parse_from_YAML
from zExceptions import Unauthorized
from zope.component import getUtility, createObject
from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent

#from js.leaflet import leaflet
#from plone.fanstatic import groups
#groups.append(leaflet)

from plone.z3cform.layout import wrap_form
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form import subform

from g24.elements.interfaces import IBasetype
from g24.elements.behaviors import ISharingbox
from g24.elements.behaviors import IBase
from g24.elements.behaviors import IEvent
from g24.elements.behaviors import IPlace
import os

template_path = os.path.dirname(__file__)


class SharingboxSubForm(subform.EditSubForm):
    """z3cform based Place subform"""
    template = ViewPageTemplateFile('subform.pt', template_path)
    title = u"Sharingbox"
    fields = field.Fields(ISharingbox)
    prefix = 'shbx'
    ignoreContext = True


class ASubForm(subform.EditSubForm):
    template = ViewPageTemplateFile('subform.pt', template_path)

    def __init__(self, context, request, form, iface, ignore_ctx):
        self.fields = field.Fields(iface)
        if not ignore_ctx:
            # if not addform (ignore_ctx=True)
            # ignore_ctx, if not provided
            ignore_ctx = not iface.providedBy(context)
        self.ignoreContext = ignore_ctx
        super(ASubForm, self).__init__(context, request, form)

#    def getContent(self):
#        super(ASubForm, self).getContent()
#    def update(self):
#        super(ASubForm, self).update()


class BaseSubForm(ASubForm):
    """z3cform based Place subform"""
    title = u"Base"
    prefix = 'base'


class EventSubForm(ASubForm):
    title = u"Event"
    prefix = 'event'

    def update(self):
        super(EventSubForm, self).update()
        # Set widget parameters, as plone.autoform doesn't support subforms yet
        # (not: ObjectSubForm, which is something else).
        widgets = self.widgets
        widgets['start'].first_day = first_weekday_sun0
        widgets['end'].first_day = first_weekday_sun0
        widgets['recurrence'].first_day = first_weekday_sun0
        widgets['recurrence'].start_field = 'start'  # Plain z3cform seems not
                                                     # to prefix schema fields


class PlaceSubForm(ASubForm):
    title = u"Place"
    prefix = 'place'


class ASharingboxForm(object):
    """z3cform Sharingbox"""
    template = ViewPageTemplateFile('editform.pt', template_path)
    fields = field.Fields(IBasetype)
    prefix = 'shbx'
    subforms = []

    def update_subforms(self, context, request, ignore_ctx):
        self.subforms = [
            SharingboxSubForm(context, request, self),
            BaseSubForm(context, request, self, IBase, ignore_ctx),
            EventSubForm(context, request, self, IEvent, ignore_ctx),
            PlaceSubForm(context, request, self, IPlace, ignore_ctx),
        ]
        [subform.update() for subform in self.subforms]

    def form_next(self):
        return

#    @button.buttonAndHandler(u'Save')
#    def handleSave(self, action):
#        data, errors = self.extractData()
#        if errors:
#            return False
#        self.form_next()
#
#    @button.buttonAndHandler(u'Cancel')
#    def handleCancel(self, action):
#        self.form_next()


class SharingboxEditForm(ASharingboxForm, form.EditForm):
    """z3cform Sharingbox"""
    #ignoreContext = False

    def update(self):
        super(SharingboxEditForm, self).update()
        context = self.context
        request = self.request
        ignore_ctx = self.ignoreContext
        self.update_subforms(context, request, ignore_ctx)

SharingboxEditFormView = wrap_form(SharingboxEditForm)


class SharingboxAddForm(ASharingboxForm, form.AddForm):
    """z3cform Sharingbox add form"""
    #ignoreContext = True

    def update(self):
        super(SharingboxAddForm, self).update()
        context = self.context
        request = self.request
        ignore_ctx = self.ignoreContext
        self.update_subforms(context, request, ignore_ctx)

SharingboxAddFormView = wrap_form(SharingboxAddForm)


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
    """Edit the attributes of an object.

    :param data:    Flat data structure:   {fieldname: value}
    :type data: dict

    :param order:   Optional list of attribute names to be set in the defined
                    order. If a attribute defined in order isn't found in data,
                    it is deleted from the object.
    :type order: list

    :param ignores: Optional list of attribute names to be ignored.
    :type ignores: list

    """
    if not order: order = []
    if not ignores: ignores = []

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
        if not attr: attr = self.defaults[key]
        if isinstance(attr, RichTextValue): # TODO: yafowil should return unicode object here...
            attr = attr.output
        return attr
