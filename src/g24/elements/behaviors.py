from zope import schema
from zope.interface import alsoProvides
from plone.directives import form
from plone.app.textfield import RichText
from g24.elements import messageFactory as _


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
        required = True
        )
alsoProvides(IRichText, form.IFormFieldProvider)
