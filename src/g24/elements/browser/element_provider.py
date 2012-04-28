from Acquisition import Explicit
from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView
from zope.contentprovider.interfaces import IContentProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ElementProvider(Explicit):
    implements(IContentProvider)
    adapts(Interface, IBrowserRequest, IBrowserView)
    template = ViewPageTemplateFile(u'element_provider.pt')

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.context = context
        self.request = request

    def render(self):
        return self.template(self)
