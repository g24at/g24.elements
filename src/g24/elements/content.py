from plone.directives import form
from z3c.form import field
from plone.app.textfield import RichText
from g24.elements import messageFactory as _

from plone.z3cform import layout

class IBasetype(form.Schema):
    """A folder that can contain cinemas
    """

    text = RichText(
            title=_(u"Body text"),
            description=_(u"Main text of this content node."),
            required=False
        )

class BasetypeForm(form.Form):
    fields = field.Fields(IBasetype)

BasetypeFormView = layout.wrap_form(BasetypeForm)
