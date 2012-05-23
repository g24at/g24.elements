from zope import schema
from zope.interface import alsoProvides, Interface, implements
from zope.component import adapts
from plone.directives import form
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
from z3c.form.browser.textlines import TextLinesFieldWidget

from g24.elements.interfaces import IBasetypeAccessor
from g24.elements.instancebehaviors import enable_behaviors, disable_behaviors
from g24.elements import messageFactory as _



class IBasetype(form.Schema):
    """ g24.elements Basetype content.
    """


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


class BaseBehavior(object):

    def __init__(self, context):
        self.context = context

    def _get_subjects(self):
        return self.context.subject
    def _set_subjects(self, value):
        self.context.subject = value
    subjects = property(_get_subjects, _set_subjects)

    def _get_text(self):
        return self.context.text
    def _set_text(self, value):
        self.context.text = value
    text = property(_get_text, _set_text)



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


    def __getattr__(self, name):
        bm = self._behavior_map
        if name in bm: # adapt object with behavior and return the attribute
           behavior = bm[name](self.context, None)
           if behavior: return getattr(behavior, name, None)
        return None

    def __setattr__(self, name, value):
        fl = self._feature_list
        bm = self._behavior_map
        if name in fl: # set the features by adding/removing behaviors
            object.__setattr__(self, name, value)
        elif name in bm: # set the attributes on behaviors
            behavior = bm[name](self.context, None)
            if behavior: setattr(behavior, name, value)

    def __delattr__(self, name):
        bm = self._behavior_map
        if name in bm:
           behavior = bm[name](self.context, None)
           if behavior: delattr(behavior, name)


    def get_is_title(self):
        return ITitle.providedBy(self.context)
    def set_is_title(self, value):
        if value:
            enable_behaviors(self.context, TITLE_BEHAVIORS, TITLE_INTERFACES)
        else:
            disable_behaviors(self.context, TITLE_BEHAVIORS, TITLE_INTERFACES)
    is_title = property(get_is_title, set_is_title)

    def get_is_event(self):
        return IDXEvent.providedBy(self.context)
    def set_is_event(self, value):
        if value:
            enable_behaviors(self.context, EVENT_BEHAVIORS, EVENT_INTERFACES)
        else:
            disable_behaviors(self.context, EVENT_BEHAVIORS, EVENT_INTERFACES)
    is_event = property(get_is_event, set_is_event)

    def get_is_place(self):
        return IPlace.providedBy(self.context)
    def set_is_place(self, value):
        if value:
            enable_behaviors(self.context, PLACE_BEHAVIORS, PLACE_INTERFACES)
        else:
            disable_behaviors(self.context, PLACE_BEHAVIORS, PLACE_INTERFACES)
    is_place = property(get_is_place, set_is_place)
