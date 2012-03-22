from plone.directives import form
from plone.app.textfield import RichText
from g24.elements import messageFactory as _

class IBasetype(form.Schema):
    """A folder that can contain cinemas
    """

    text = RichText(
            title=_(u"Body text"),
            description=_(u"Main text of this content node."),
            required=False
        )
