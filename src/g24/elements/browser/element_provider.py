from Products.Five.browser import BrowserView
from plone.uuid.interfaces import IUUID
from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView
from zope.contentprovider.interfaces import IContentProvider
from zope.security import checkPermission
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ElementProvider(BrowserView):
    implements(IContentProvider)
    adapts(Interface, IBrowserRequest, IBrowserView)
    template = ViewPageTemplateFile(u'element_provider.pt')

    def __init__(self, context, request, view):
        self.context = context.aq_base # make, context isn't on parent
        self.request = request

    @property
    def uuid(self):
        uuid = IUUID(self.context, None)
        return uuid

    @property
    def can_add(self):
        return True # TODO: fix me
        return checkPermission('g24.AddBasetype', self.context)

    @property
    def can_edit(self):
        return True # TODO: fix me
        return checkPermission('g24.ModifyBasetype', self.context)

    def render(self):
        return self.template(self)
