from zope import schema
from zope.interface import alsoProvides, Interface, implements
from zope.component import adapts
from plone.directives import form
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.textfield import RichText
from g24.elements.interfaces import IBasetypeAccessor
from g24.elements import messageFactory as _
from plone.app.event.dx.behaviors import (
    IEventBasic,
    IEventRecurrence,
    IEventLocation
)


class IBasetype(form.Schema):
    """ g24.elements Basetype content.
    """

class ITitle(form.Schema):
    title = schema.TextLine(
        title = _(u'label_title', default=u'Title'),
        description = _(u'help_title', default=u'The title of your post.'),
        required = True
        )
    form.order_before(title = '*')
alsoProvides(ITitle, form.IFormFieldProvider)


class IRichText(form.Schema):
    text = RichText(
        title = _(u'label_richtext', default=u'Body text'),
        description = _(u'help_richtext', default=u'Main text of this content node.'),
        required = True,
        default_mime_type='text/html',
        output_mime_type='text/html',
        allowed_mime_types=['text/html', 'text/plain', 'text/x-rst', 'text/restructured'],
        )
alsoProvides(IRichText, form.IFormFieldProvider)


class IPlace(Interface):
    """ Behavior marker interface for places. """


class BasetypeAccessor(object):
    adapts(IBasetype)
    implements(IBasetypeAccessor)

    def __init__(self, context):
        object.__setattr__(self, 'context', context)

        bm = dict(
            title=ITitle,
            text=IRichText,
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
        if name in bm:
           behavior = bm[name](self.context, None)
           if behavior: return getattr(behavior, name, None)
        return None

    def __setattr__(self, name, value):
        bm = self._behavior_map
        if name in bm:
            behavior = bm[name](self.context, None)
            if behavior: setattr(behavior, name, value)

    def __delattr__(self, name):
        bm = self._behavior_map
        if name in bm:
           behavior = bm[name](self.context, None)
           if behavior: delattr(behavior, name)

    @property
    def is_title(self):
        return ITitle.providedBy(self.context)

    @property
    def is_event(self):
        return IDXEvent.providedBy(self.context)

    @property
    def is_place(self):
        return IPlace.providedBy(self.context)
