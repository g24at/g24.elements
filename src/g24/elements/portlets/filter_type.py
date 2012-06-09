from zope.formlib import form
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from g24.elements import messageFactory as _

class IFilterType(IPortletDataProvider):
    """ Portlet Interface
    """

class Assignment(base.Assignment):
    implements(IFilterType)

    @property
    def title(self):
        return _(u"portlet_filter_type_title", u"Filter type portlet")

class AddForm(base.NullAddForm):
    form_fields = form.Fields(IFilterType)
    label = _(u"portlet_filter_type_label_add",
              u"""Add portlet to filter after g24.element type in the
                  streamview.""")

    def create(self):
        return Assignment()

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('filter_type.pt')
