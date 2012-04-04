from plone.directives import form
from z3c.form import field, button
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

    @button.buttonAndHandler(u'Submit')
    def handleApply(self, action):
        data, errors = self.extractData()
        # do something

BasetypeFormView = layout.wrap_form(BasetypeForm)
"""
class BasetypeFormView(layout.FormWrapper):

    def __init__(self, request, context):
        self.request = request
        self.context = context

    def __call__(self):
        context = self.context
        import pdb;pdb.set_trace()
        return layout.wrap_form(BasetypeForm)(self.context, self.request).__call__()
"""
