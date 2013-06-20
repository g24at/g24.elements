from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import ulocalized_time
from plone.app.event.base import DT
from plone.app.event.dx.behaviors import IEventBasic
from plone.app.event.dx.behaviors import IEventLocation
from plone.app.event.dx.behaviors import IEventRecurrence
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.event.dx.interfaces import IDXEventLocation
from plone.app.event.dx.interfaces import IDXEventRecurrence
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.indexer import indexer
from plone.supermodel import model
from plone.uuid.interfaces import IUUID
from z3c.form.browser.textlines import TextLinesFieldWidget
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides, Interface, implements
from collective.address.behaviors import IAddress
from collective.geolocationbehavior.geolocation import IGeolocatable


from g24.elements import safe_decode
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


class IBase(model.Schema):

    title = schema.TextLine(
        title = _(u'label_title', default=u'Title'),
        description = _(u'help_title', default=u'The title of your post.'),
        required = True
        )
    form.order_before(title = '*')

    text = schema.Text(
        title = _(u'label_richtext', default=u'Body text'),
        description = _(u'help_richtext', default=u'Main text of this content node.'),
        required = True,
    )

    #    text = RichText(
    #        title = _(u'label_richtext', default=u'Body text'),
    #        description = _(u'help_richtext', default=u'Main text of this content node.'),
    #        required = True,
    #        default_mime_type='text/html',
    #        output_mime_type='text/html',
    #        allowed_mime_types=['text/html', 'text/plain', 'text/x-rst', 'text/restructured'],
    #        )

    subjects = schema.Tuple(
        title = _(u'label_categories', default=u'Categories'),
        description = _(u'help_categories', default=u'Also known as keywords, tags or labels, these help you categorize your content.'),
        value_type = schema.TextLine(),
        required = False,
        missing_value = (),
        )
    form.widget(subjects = TextLinesFieldWidget)
alsoProvides(IBase, IFormFieldProvider)


class IThread(Interface):
    """Behavior marker interface for threads."""

class IPlace(IAddress, IGeolocatable):
    """Behavior marker interface for places."""

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


EVENT_INTERFACES = [IDXEvent, IDXEventRecurrence, IDXEventLocation]
EVENT_BEHAVIORS = ['plone.app.event.dx.behaviors.IEventBasic',
                   'plone.app.event.dx.behaviors.IEventRecurrence',
                   'plone.app.event.dx.behaviors.IEventLocation']

THREAD_INTERFACES =  [IThread,]
THREAD_BEHAVIORS = ['g24.elements.behaviors.IThread',]

PLACE_INTERFACES = [IPlace,]
PLACE_BEHAVIORS = ['g24.elements.behaviors.IPlace',]


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
        >>> acc.is_location

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
          File "/home/thet-data/dotfiles-thet/dotfiles.buildout/eggs/Paste-1.7.5.1-py2.7.egg/paste/evalexception/evalcontext.py", line 37, in exec_expr
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
            timezone=IEventBasic,
            whole_day=IEventBasic,
            recurrence=IEventRecurrence,
            location=IEventLocation,
            altitude=IPlace,
            latitude=IPlace,
            longitude=IPlace
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
        if name in bm: # adapt object with behavior and return the attribute
           behavior = bm[name](self.context, None)
           if behavior:
               value = getattr(behavior, name, None)
               return value
        return None

    def __setattr__(self, name, value):
        fl = self._feature_list
        bm = self._behavior_map
        if name in fl: # set the features by adding/removing behaviors
            object.__setattr__(self, name, value)
        elif name in bm: # set the attributes on behaviors
            behavior = bm[name](self.context, None)
            if behavior:
                # all strings go unicode
                value = safe_decode(value)
                setattr(behavior, name, value)

    def __delattr__(self, name):
        bm = self._behavior_map
        if name in bm:
            behavior = bm[name](self.context, None)
            if behavior: delattr(behavior, name)
        try:
            # try ro delete the attribute also on the context
            delattr(self.context, name)
        except AttributeError:
            # attribute not set:
            pass


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
            pt = getToolByName(self.context, 'portal_transforms')
            data = pt.convertTo('text/plain', value, mimetype='text/html')
            text = data.getData()
            return text
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
            disable_behaviors(self.context, THREAD_BEHAVIORS, THREAD_INTERFACES)

    @property
    def is_event(self):
        return IDXEvent.providedBy(self.context)
    @is_event.setter
    def is_event(self, value):
        if value:
            enable_behaviors(self.context, EVENT_BEHAVIORS, EVENT_INTERFACES)
        else:
            # delete the orphaned attribute from an deleted behaviors
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
            try: delattr(self.context, attr)
            except: pass
