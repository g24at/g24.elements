from zope.security import checkPermission
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.navigation.navtree import buildFolderTree
from g24.elements.content import IBasetype

BOTTOMLEVEL = 6

class ThreadView(BrowserView):

    def itemtree(self):
        context = self.context
        query = {}
        query['object_provides'] = IBasetype.__identifier__
        query['path'] = {'query': '/'.join(context.getPhysicalPath())}
        #query['path']['depth'] = BOTTOMLEVEL
        query['sort_on'] = 'created'
        query['sort_order'] = 'reverse'

        return buildFolderTree(context, obj=context, query=query)

    def start_recurse(self):
        return self.recurse(children=self.itemtree().get('children', []),
            level=1, bottomLevel=self.bottomlevel)

    def can_add(self, parent):
        return checkPermission('cmf.AddPortalContent', parent)

    def can_edit(self, context):
        return checkPermission('cmf.ModifyPortalContent', context)

    bottomlevel = BOTTOMLEVEL
    recurse = ViewPageTemplateFile('threadview_recurse.pt')
