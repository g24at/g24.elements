from zope import schema
from zope.interface import alsoProvides, Interface, implements
from zope.component import adapts
from plone.directives import form
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.textfield import RichText
from z3c.form.browser.textlines import TextLinesFieldWidget

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


class BasetypeAccessor(object):
    adapts(IBasetype)
    implements(IBasetypeAccessor)

    def __init__(self, context):
        object.__setattr__(self, 'context', context)

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
