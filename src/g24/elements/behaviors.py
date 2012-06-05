from zope import schema
from zope.interface import alsoProvides, Interface, implements
from zope.component import adapts
from zope.component.hooks import getSite
from plone.app.event.dx.behaviors import (
    IEventBasic,
    IEventRecurrence,
    IEventLocation
)
from plone.app.event.dx.interfaces import (
    IDXEvent,
    IDXEventRecurrence,
    IDXEventLocation
)
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue
from plone.app.textfield.interfaces import ITransformer
from plone.directives import form
from plone.indexer import indexer
from z3c.form.browser.textlines import TextLinesFieldWidget

from g24.elements.interfaces import (
    IBasetype,
    IBasetypeAccessor
)
from g24.elements.instancebehaviors import enable_behaviors, disable_behaviors
from g24.elements import messageFactory as _



class IBase(form.Schema):
    text = RichText(
        title = _(u'label_richtext', default=u'Body text'),
        description = _(u'help_richtext', default=u'Main text of this content node.'),
        required = True,
        default_mime_type='text/html',
        output_mime_type='text/html',
        allowed_mime_types=['text/html', 'text/plain', 'text/x-rst', 'text/restructured'],
        )

    subjects = schema.Tuple(
        title = _(u'label_categories', default=u'Categories'),
        description = _(u'help_categories', default=u'Also known as keywords, tags or labels, these help you categorize your content.'),
        value_type = schema.TextLine(),
        required = False,
        missing_value = (),
        )
    form.widget(subjects = TextLinesFieldWidget)
alsoProvides(IBase, form.IFormFieldProvider)


class ITitle(form.Schema):
    title = schema.TextLine(
        title = _(u'label_title', default=u'Title'),
        description = _(u'help_title', default=u'The title of your post.'),
        required = True
        )
    form.order_before(title = '*')
alsoProvides(ITitle, form.IFormFieldProvider)


class IPlace(Interface):
    """ Behavior marker interface for places. """


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


EVENT_INTERFACES = (IDXEvent, IDXEventRecurrence, IDXEventLocation)
EVENT_BEHAVIORS = ('plone.app.event.dx.behaviors.IEventBasic',
                   'plone.app.event.dx.behaviors.IEventRecurrence',
                   'plone.app.event.dx.behaviors.IEventLocation')

TITLE_INTERFACES =  (ITitle,)
TITLE_BEHAVIORS = ('g24.elements.behaviors.ITitle',)

PLACE_INTERFACES = (IPlace,)
PLACE_BEHAVIORS = ('g24.elements.behaviors.IPlace',)


class BasetypeAccessor(object):
    """ Accessor object for Basetype objects.
        It adapts the object to it's behaviors for proper attribute access.

        If you also have to set Basetype features (behaviors), do that first!
        This way, setting of attributes for a specific feature won't fail.

        TODO: Create a mock object / real object with is_event feature enabled.
        >>> context
        <Container at /Plone/stream>
        >>> from g24.elements.interfaces import IBasetype
        >>> IBasetype.providedBy(context)
        True
        >>> from g24.elements.interfaces import IBasetypeAccessor
        >>> IBasetypeAccessor(context)
        <g24.elements.behaviors.BasetypeAccessor object at 0x7f77bc2fb550>
        >>> acc = IBasetypeAccessor(context)
        >>> acc.is_event
        True
        >>> acc.is_title
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
        >>> acc.is_title = True
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
        fl = ['is_title', 'is_event', 'is_place']
        object.__setattr__(self, '_feature_list', fl)

        # mapping of behavior attributes to behaviors
        bm = dict(
            title=ITitle,
            text=IBase,
            subjects=IBase,
            start=IEventBasic,
            end=IEventBasic,
            timezone=IEventBasic,
            whole_day=IEventBasic,
            recurrence=IEventRecurrence,
            location=IEventLocation
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
               if isinstance(value, RichTextValue):
                   value = value.output
                   if not isinstance(value, unicode):
                       value = value.decode('utf-8')
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
                if name == 'text':
                    # text must be a RichTextValue
                    if not isinstance(value, unicode):
                        # we assume values to be utf-8 encoded.
                        value = unicode(value.decode('utf-8'))
                    value = RichTextValue(raw=value)
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
        if isinstance(value, RichTextValue):
            site = getSite()
            trans = ITransformer(site)
            value = trans(value, 'text/plain')
        # if not, do just index the value as is. (maybe attr not yet set?)
        return value

    @property
    def is_title(self):
        return ITitle.providedBy(self.context)
    @is_title.setter
    def is_title(self, value):
        if value:
            enable_behaviors(self.context, TITLE_BEHAVIORS, TITLE_INTERFACES)
        else:
            self._delattrs(['title'])
            disable_behaviors(self.context, TITLE_BEHAVIORS, TITLE_INTERFACES)

    @property
    def is_event(self):
        return IDXEvent.providedBy(self.context)
    @is_event.setter
    def is_event(self, value):
        if value:
            enable_behaviors(self.context, EVENT_BEHAVIORS, EVENT_INTERFACES)
        else:
            # delete the orphaned attribute from an deleted behavior
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
