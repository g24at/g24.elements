from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from z3c.form import form, field, button
from plone.z3cform.layout import FormWrapper, wrap_form
from g24.elements.content import IBasetype
from g24.elements import messageFactory as _

class SharingBoxForm(form.Form):
    fields = field.Fields(IBasetype)
    label = _(u"Sharing Box")
    description = _(u"Share some content with us...")
    ignoreContext = True

    def __init__(self, context, request, returnURLHint=None, full=True):
        """
        @param returnURLHint: Should we enforce return URL for this form
        @param full: Show all available fields or just required ones.
        """
        super(SharingBoxForm, self).__init__(context, request)
        self.all_fields = full
        self.returnURLHint = returnURLHint

    @property
    def action(self):
        """ Rewrite HTTP POST action.

        If the form is rendered embedded on the others pages we
        make sure the form is posted through the same view always,
        instead of making HTTP POST to the page where the form was rendered.
        """
        return self.context.portal_url() + "/@@sharingbox-form"

    @button.buttonAndHandler(u'Submit')
    def handleApply(self, action):
        data, errors = self.extractData()
        # do something

class SharingBoxFormViewFrameless(FormWrapper):
     """ Form view which renders embedded z3c.forms.
     It subclasses FormWrapper so that we can use custom frame template.
     """
     index = ViewPageTemplateFile("sharingbox_wrapper.pt")

SharingBoxFormView = wrap_form(SharingBoxForm)


class SharingBoxViewlet(BrowserView):
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.__parent__ = view
        self.manager = manager

    def create_form(self):
        """ Create a form instance.

        @return: z3c.form wrapped for view in Plone.
        """
        context = self.context.aq_inner
        returnURL = self.context.absolute_url()

        form = SharingBoxForm(context, self.request, returnURLHint=returnURL, full=False)
        
        view = SharingBoxFormViewFrameless(self.context, self.request)
        view = view.__of__(context) # Make sure acquisition chain is respected
        view.form_instance = form

        return view
