from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import ulocalized_time
from collective.address.behaviors import IAddress
from collective.geolocationbehavior.geolocation import IGeolocatable
from plone.app.event.base import DT
from plone.app.event.dx.behaviors import IEventBasic
from plone.app.event.dx.behaviors import IEventLocation
from plone.app.event.dx.behaviors import IEventRecurrence
from plone.app.event.dx.behaviors import first_weekday_sun0
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.event.dx.interfaces import IDXEventLocation
from plone.app.event.dx.interfaces import IDXEventRecurrence
from plone.app.widgets.dx import AjaxSelectWidget
from plone.app.widgets.dx import DatetimeWidget
from plone.app.widgets.dx import SelectWidget
from plone.app.widgets.interfaces import IWidgetsLayer
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.indexer import indexer
from plone.supermodel import model
from plone.uuid.interfaces import IUUID
from z3c.form.browser.textlines import TextLinesFieldWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.util import getSpecification
from z3c.form.widget import ComputedWidgetAttribute
from z3c.form.widget import FieldWidget
from zope import schema
from zope.component import adapter
from zope.component import adapts
from zope.component import provideAdapter
from zope.interface import alsoProvides, Interface, implements
from zope.interface import implementer


from g24.elements import safe_decode, safe_encode
from g24.elements.instancebehaviors import disable_behaviors
from g24.elements.instancebehaviors import enable_behaviors
from g24.elements.interfaces import IBasetype
from g24.elements.interfaces import IBasetypeAccessor
from g24.elements import messageFactory as _

#from zope.component.hooks import getSite
#from plone.app.textfield import RichText
#from plone.app.textfield.value import RichTextValue
#from plone.app.textfield.interfaces import ITransformer


def format_date(date, context):
    return ulocalized_time(DT(date), long_format=True, time_only=None,
                           context=context)


class IFeatures(model.Schema):
    """Sharingbox features marker interface."""

    is_thread = schema.Bool(
        title=_(u'label_is_thread', default=u"I'm a Thread"),
        description=_(u'help_thread', default=u"Start a new thread."),
        required=False
    )

    is_event = schema.Bool(
        title=_(u'label_is_event', default=u"I'm an Event"),
        description=_(u'help_event', default=u"Make me an event."),
        required=False
    )

    is_place = schema.Bool(
        title=_(u'label_is_place', default=u"I'm a Place"),
        description=_(
            u'help_is_place',
            default=u"Define a place with address and/or geolocation data."
        ),
        required=False
    )
alsoProvides(IFeatures, IFormFieldProvider)


def feature_thread(data):
    return IBasetypeAccessor(data.context).is_thread
provideAdapter(ComputedWidgetAttribute(
    feature_thread, field=IFeatures['is_thread']), name='default')


def feature_event(data):
    return IBasetypeAccessor(data.context).is_event
provideAdapter(ComputedWidgetAttribute(
    feature_event, field=IFeatures['is_event']), name='default')


def feature_place(data):
    return IBasetypeAccessor(data.context).is_place
provideAdapter(ComputedWidgetAttribute(
    feature_place, field=IFeatures['is_place']), name='default')


class IBase(model.Schema):

    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        description=_(u'help_title', default=u'The title of your post.'),
        required=True
        )
    form.order_before(title='*')

    text = schema.Text(
        title=_(u'label_richtext', default=u'Body text'),
        description=_(
            u'help_richtext',
            default=u'Main text of this content node.'
        ),
        required=True,
    )

    #    text = RichText(
    #        title = _(u'label_richtext', default=u'Body text'),
    #        description = _(
    #            u'help_richtext',
    #            default=u'Main text of this content node.'
    #        ),
    #        required = True,
    #        default_mime_type='text/html',
    #        output_mime_type='text/html',
    #        allowed_mime_types=[
    #            'text/html',
    #            'text/plain',
    #            'text/x-rst',
    #            'text/restructured'
    #        ],
    #    )

    subjects = schema.Tuple(
        title=_(u'label_categories', default=u'Categories'),
        description=_(
            u'help_categories',
            default=u'Also known as keywords, tags or labels, these help you '
                    u'categorize your content.'),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
        )
    form.widget('subjects', TextLinesFieldWidget)
alsoProvides(IBase, IFormFieldProvider)


class IThread(Interface):
    """Behavior marker interface for threads."""


class IEvent(IEventBasic, IEventRecurrence, IEventLocation,
             IDXEvent, IDXEventRecurrence, IDXEventLocation):
    """Behavior marker interface for events."""
    # For Plone autoform based forms. Plain z3cforms get their properties set
    # within the form's update method.
    form.widget('start', first_day=first_weekday_sun0)
    form.widget('end', first_day=first_weekday_sun0)
    form.widget('recurrence',
                start_field='IEvent.start',
                first_day=first_weekday_sun0)
alsoProvides(IEvent, IFormFieldProvider)


class IPlace(IAddress, IGeolocatable):
    """Behavior marker interface for places."""
alsoProvides(IPlace, IFormFieldProvider)


# plone.app.widgets integration

@adapter(getSpecification(IBase['subjects']), IWidgetsLayer)
@implementer(IFieldWidget)
def SubjectsFieldWidget(field, request):
    widget = FieldWidget(field, AjaxSelectWidget(request))
    widget.vocabulary = 'plone.app.vocabularies.Keywords'
    return widget


@adapter(getSpecification(IEvent['timezone']), IWidgetsLayer)
@implementer(IFieldWidget)
def TimezoneFieldWidget(field, request):
    widget = FieldWidget(field, SelectWidget(request))
    return widget


@adapter(getSpecification(IEvent['location']), IWidgetsLayer)
@implementer(IFieldWidget)
def LocationFieldWidget(field, request):
    widget = FieldWidget(field, AjaxSelectWidget(request))
    widget.vocabulary = 'g24.elements.Locations'
    return widget


@adapter(getSpecification(IPlace['country']), IWidgetsLayer)
@implementer(IFieldWidget)
def CountryFieldWidget(field, request):
    widget = FieldWidget(field, SelectWidget(request))
    #widget.vocabulary = 'collective.address.CountryVocabulary'
    return widget


@adapter(getSpecification(IEvent['start']), IWidgetsLayer)
@implementer(IFieldWidget)
def StartFieldWidget(field, request):
    widget = FieldWidget(field, DatetimeWidget(request))
    return widget


@adapter(getSpecification(IEvent['end']), IWidgetsLayer)
@implementer(IFieldWidget)
def EndFieldWidget(field, request):
    widget = FieldWidget(field, DatetimeWidget(request))
    return widget


#class IPlace(model.Schema):
#    """Behavior marker interface for places."""
#    altitude = schema.Float(title = _(u'Altitude'))
#    latitude = schema.Float(title = _(u'Latitude'))
#    longitude = schema.Float(title = _(u'Longitude'))


@indexer(IBasetype)
def searchable_text_indexer(obj):
    acc = IBasetypeAccessor(obj)
    text = acc.plaintext
    title = acc.title

    # concat, but only if item not ''
    return u' '.join([item for item in [title, text] if item])


@indexer(IBasetype)
def keyword_indexer(obj):
    acc = IBasetypeAccessor(obj)
    return acc.subjects


#EVENT_INTERFACES = [IDXEvent, IDXEventRecurrence, IDXEventLocation]
#EVENT_BEHAVIORS = ['plone.app.event.dx.behaviors.IEventBasic',
#                   'plone.app.event.dx.behaviors.IEventRecurrence',
#                   'plone.app.event.dx.behaviors.IEventLocation']

EVENT_INTERFACES = [IEvent, ]
EVENT_BEHAVIORS = ['g24.elements.behaviors.IEvent', ]

THREAD_INTERFACES = [IThread, ]
THREAD_BEHAVIORS = ['g24.elements.behaviors.IThread', ]

PLACE_INTERFACES = [IPlace, ]
PLACE_BEHAVIORS = ['g24.elements.behaviors.IPlace', ]


class BasetypeAccessor(object):
    """ Accessor object for Basetype objects.
        It adapts the object to it's behaviors for proper attribute access.

        If you also have to set Basetype features (behaviors), do that first!
        This way, setting of attributes for a specific feature won't fail.

        TODO: Create a mock object / real object with is_event feature enabled.
        >>> context
        <Container at /Plone/posts>
        >>> from g24.elements.interfaces import IBasetype
        >>> IBasetype.providedBy(context)
        True
        >>> from g24.elements.interfaces import IBasetypeAccessor
        >>> IBasetypeAccessor(context)
        <g24.elements.behaviors.BasetypeAccessor object at 0x7f77bc2fb550>
        >>> acc = IBasetypeAccessor(context)
        >>> acc.is_event
        True
        >>> acc.is_thread
        False
        >>> acc.is_place
        False
        >>> acc.is_place
        False

        Nonexistent throws no Error
        TODO: ok? ^^
        >>> acc.is_SOMETHING

        Setting something, where the feature is not enabled, doesn't work.
        So set the features first!
        >>> acc.title = 'postgarasch'
        >>> acc.title

        Set the feature:
        >>> acc.is_thread = True
        >>> acc.title = 'postgarasch'
        >>> acc.title
        'postgarasch'

        This is an event.
        >>> acc.is_event
        True
        >>> acc.start
        datetime.datetime(2012, 5, 30, 0, 0, tzinfo=<UTC>)

        Disable the event feature.
        >>> acc.is_event = False
        >>> acc.start

        But still, the attribute is set on the context!
        >>> context.start
        datetime.datetime(2012, 5, 30, 0, 0, tzinfo=<UTC>)

        So do a final cleanup to delete those attributes as well.
        Why? Because Zope's catalog index looks for object attributes to index.
        >>> acc.cleanup()
        >>> context.start
        Traceback (most recent call last):
            ....
            exec code in self.namespace, self.globs
          File "<web>", line 1, in <module>
        AttributeError: start
    """
    adapts(IBasetype)
    implements(IBasetypeAccessor)

    def __init__(self, context):
        object.__setattr__(self, 'context', context)

        # definition of feature attributes
        fl = ['is_thread', 'is_event', 'is_place']
        object.__setattr__(self, '_feature_list', fl)

        # mapping of behavior attributes to behaviors
        bm = dict(
            title=IBase,
            text=IBase,
            subjects=IBase,
            start=IEventBasic,
            end=IEventBasic,
            whole_day=IEventBasic,
            open_end=IEventBasic,
            timezone=IEventBasic,
            recurrence=IEventRecurrence,
            location=IEventLocation,
            geolocation=IGeolocatable,
            street=IAddress,
            zip_code=IAddress,
            city=IAddress,
            country=IAddress,
        )
        object.__setattr__(self, '_behavior_map', bm)

    #    def cleanup(self):
    #        bm = self._behavior_map
    #        for attr, behavior in bm.items():
    #            if not behavior.providedBy(self.context):
    #                # delete the orphaned attribute from an deleted behavior
    #                try:
    #                    delattr(self.context, attr)
    #                except:
    #                    pass

    def __getattr__(self, name):
        bm = self._behavior_map
        if name in bm:  # adapt object with behavior and return the attribute
            behavior = bm[name](self.context, None)
            if behavior:
                value = getattr(behavior, name, None)
                return value
        return None

    def __setattr__(self, name, value):
        fl = self._feature_list
        bm = self._behavior_map
        if name in fl:  # set the features by adding/removing behaviors
            object.__setattr__(self, name, value)
        elif name in bm:  # set the attributes on behaviors
            behavior = bm[name](self.context, None)
            if behavior:
                # all strings go unicode
                value = safe_decode(value)
                setattr(behavior, name, value)

    def __delattr__(self, name):
        bm = self._behavior_map
        if name in bm:
            behavior = bm[name](self.context, None)
            if behavior:
                delattr(behavior, name)
        try:
            # try ro delete the attribute also on the context
            delattr(self.context, name)
        except AttributeError:
            # attribute not set:
            pass

    @property
    def latitude(self):
        return self.is_place and self.geolocation.latitude or None

    @property
    def longitude(self):
        return self.is_place and self.geolocation.longitude or None

    @property
    def plaintext(self):
        behavior = IBase(self.context, None)
        value = getattr(behavior, 'text', None)
        ## TODO: reenable transform
        #return value

        #if isinstance(value, RichTextValue):
        #    site = getSite()
        #    trans = ITransformer(site)
        #    value = trans(value, 'text/plain')

        if value:
            value = safe_encode(value)
            pt = getToolByName(self.context, 'portal_transforms')
            data = pt.convertTo('text/plain', value, mimetype='text/html')
            text = data.getData()
            return safe_decode(text)
        return None

    # ro properties
    #
    @property
    def uid(self):
        return IUUID(self.context, None)

    @property
    def url(self):
        return self.context.absolute_url()

    @property
    def created(self):
        return format_date(self.context.created(), self.context)

    @property
    def last_modified(self):
        return format_date(self.context.modified(), self.context)

    # rw properties
    #
    @property
    def is_thread(self):
        # TODO: rethink.
        # Currently: manually set IThread
        # Alternative:
        #   If posting has more than 2 children: True
        #   If not: False
        return IThread.providedBy(self.context)

    @is_thread.setter
    def is_thread(self, value):
        if value:
            enable_behaviors(self.context, THREAD_BEHAVIORS, THREAD_INTERFACES)
        else:
            disable_behaviors(self.context,
                              THREAD_BEHAVIORS, THREAD_INTERFACES)

    @property
    def is_event(self):
        return IDXEvent.providedBy(self.context)

    @is_event.setter
    def is_event(self, value):
        if value:
            enable_behaviors(self.context, EVENT_BEHAVIORS, EVENT_INTERFACES)
        else:
            # delete orphaned attributes from disabled behaviors
            # so that indexers do not index them.
            self._delattrs(['start', 'end', 'timezone', 'whole_day',
                            'recurrence', 'location'])
            disable_behaviors(self.context, EVENT_BEHAVIORS, EVENT_INTERFACES)

    @property
    def is_place(self):
        return IPlace.providedBy(self.context)

    @is_place.setter
    def is_place(self, value):
        if value:
            enable_behaviors(self.context, PLACE_BEHAVIORS, PLACE_INTERFACES)
        else:
            disable_behaviors(self.context, PLACE_BEHAVIORS, PLACE_INTERFACES)

    def _delattrs(self, attrs):
        for attr in attrs:
            # self.context.title cannot be deleted. after deleting, it will be
            # instantly magically set to ''
            try:
                delattr(self.context, attr)
            except:
                pass
