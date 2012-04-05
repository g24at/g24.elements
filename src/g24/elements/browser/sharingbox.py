from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from plone.directives import form
from plone.z3cform.layout import FormWrapper, wrap_form
from plone.dexterity.utils import getAdditionalSchemata
from g24.elements.content import IBasetype
from g24.elements import messageFactory as _

from plone.directives.dexterity import AddForm, EditForm


class SharingBoxBaseForm(object):
    #label = _(u"Sharing Box")
    #description = _(u"Share some content with us...")

    @property
    def additionalSchemata(self):
        # TODO: cache me! i'm called 2 times when rendering and 6 times when
        # saved + rendered

        # expand the list of schematas with those provided by the context
        context = self.context
        add_schemata = []
        if IBasetype.providedBy(context):
            add_schemata = getAdditionalSchemata(context=context)
        else:
            # default portal type
            add_schemata = getAdditionalSchemata(
                                portal_type='g24.elements.basetype')
        add_schemata = [sch for sch in add_schemata if sch.getName() not in
                        self.schema_blacklist]
        return add_schemata


class SharingBoxEditForm(SharingBoxBaseForm, EditForm):

    def __init__(self, context, request,
                 schema_blacklist=[], field_blacklist=[], *args, **kwargs):
        self.schema_blacklist = schema_blacklist
        self.field_blacklist = field_blacklist
        super(SharingBoxEditForm, self).__init__(context, request, *args, **kwargs)

    def updateFields(self):
        super(SharingBoxEditForm, self).updateFields()
        for key in self.fields.keys():
            if key in self.field_blacklist:
                form.omitted(key) # TODO: test multiple field_blacklist keys


class SharingBoxAddForm(SharingBoxBaseForm, AddForm):

    portal_type = 'g24.elements.basetype'

    def __init__(self, context, request,
                 schema_blacklist=[], field_blacklist=[], *args, **kwargs):
        self.schema_blacklist = schema_blacklist
        self.field_blacklist = field_blacklist
        super(SharingBoxAddForm, self).__init__(context, request, *args, **kwargs)

    def updateFields(self):
        super(SharingBoxAddForm, self).updateFields()
        for key in self.fields.keys():
            if key in self.field_blacklist:
                form.omitted(key) # TODO: test multiple field_blacklist keys


SharingBoxFormView = wrap_form(SharingBoxEditForm)
class SharingBoxFormViewFrameless(FormWrapper):
     """ Form view which renders embedded z3c.forms.
     It subclasses FormWrapper so that we can use custom frame template.
     """
     index = ViewPageTemplateFile("sharingbox_wrapper.pt")


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

        form = SharingBoxAddForm(context, self.request, schema_blacklist='IDublinCore')

        view = SharingBoxFormViewFrameless(self.context, self.request)
        view = view.__of__(context) # Make sure acquisition chain is respected
        view.form_instance = form

        return view
