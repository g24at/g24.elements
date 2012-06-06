from Acquisition import aq_parent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.navigation.navtree import buildFolderTree
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
from g24.elements.interfaces import IBasetype

BOTTOMLEVEL = 6

class ThreadView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

        #parent = getattr(context, '__parent__', None)
        #parent = self.context.getParentNode()
        parent = aq_parent(self.context)
        parent_url = None
        if parent and IBasetype.providedBy(parent):
            parent_url = parent.absolute_url()
        self.parent_url = parent_url

        print("ThreadView __init__ %s" % str(context))

    def itemtree(self):
        context = self.context
        query = {}
        query['object_provides'] = IBasetype.__identifier__
        query['path'] = {'query': '/'.join(context.getPhysicalPath())}
        #query['path']['depth'] = BOTTOMLEVEL
        query['sort_on'] = 'created'
        #query['sort_order'] = 'reverse' ## reverse just doesn't feel natural.
        print("ThreadView itemtree %s" % str(context))

        return buildFolderTree(context, obj=context, query=query)

    def start_recurse(self):
        print("ThreadView start_recurse %s" % str(self.context))
        return self.recurse(children=self.itemtree().get('children', []),
            level=1, bottomLevel=self.bottomlevel)

    def element_provider(self, context):
        print("ThreadView element_provider %s" % str(context))
        provider = getMultiAdapter((context, self.request, self),
                                   IContentProvider,
                                   name=u"element_provider")
        return provider.render()

    bottomlevel = BOTTOMLEVEL
    recurse = ViewPageTemplateFile('threadview_recurse.pt')
