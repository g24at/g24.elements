from zope import schema
from zope.interface import alsoProvides, Interface, implements
from zope.component import adapts
from plone.directives import form
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.textfield import RichText
from g24.elements.content import IBasetype
from g24.elements.interfaces import IBasetypeAccessor
from g24.elements import messageFactory as _
from plone.app.event.dx.behaviors import (
    IEventBasic,
    IEventRecurrence,
    IEventLocation
)


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


def is_title(context):
    return ITitle.providedBy(context)

def is_event(context):
    return IDXEvent.providedBy(context)

def is_place(context):
    return IPlace.providedBy(context)


class BasetypeAccessor(object):
    adapts(IBasetype)
    implements(IBasetypeAccessor)

    def __init__(self, context):
        self.context = context
        self._behavior_map = dict(
            title=ITitle,
            text=IRichText,
            start=IEventBasic,
            end=IEventBasic,
            timezone=IEventBasic,
            whole_day=IEventBasic,
            recurrence=IEventRecurrence,
            location=IEventLocation
        )

    def __getattr__(self, name):
        bm = self._behavior_map
        return name in bm and getattr(bm[name](self.context), name, None)\
                or None

    def __setattr__(self, name, value):
        bm = self._behavior_map
        if name in bm:
            setattr(bm[name](self.context), name, value)
