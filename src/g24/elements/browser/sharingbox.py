from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.directives import form
from plone.z3cform.layout import wrap_form
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

    """
    def updateActions(self):
        super(SharingBoxEditForm, self).updateActions()
        import pdb;pdb.set_trace()
    """

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


SharingBoxAddFormView = wrap_form(SharingBoxAddForm)
SharingBoxEditFormView = wrap_form(SharingBoxEditForm)

class SharingBoxAddFormViewFrameless(SharingBoxAddFormView):
    """ BaseType add form without rendering in main template.
    """
    #index = ViewPageTemplateFile("sharingbox.pt")
    index = ViewPageTemplateFile("sharingbox_custom.pt")

    """
    def update(self):
        super(SharingBoxAddFormViewFrameless, self).update()
        import pdb;pdb.set_trace()
    """

class SharingBoxEditFormViewFrameless(SharingBoxEditFormView):
    """ BaseType edit form without rendering in main template.
    """
    #index = ViewPageTemplateFile("sharingbox.pt")
    index = ViewPageTemplateFile("sharingbox_custom.pt")

    """
    def update(self):
        super(SharingBoxEditFormViewFrameless, self).update()
        import pdb;pdb.set_trace()
        self.widgets = self.form_instance.widgets
    """
