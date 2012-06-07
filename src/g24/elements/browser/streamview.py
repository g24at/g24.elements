from Products.CMFCore.utils import getToolByName
from plone.batching import Batch
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
from g24.elements.interfaces import IBasetype

class StreamView(BrowserView):

    def items(self, user=None, tag=None, path=False, type_=None):

        # batch paging
        b_start = 'b_start' in self.request.form and int(self.request.form['b_start']) or 0
        b_size = 10

        # filter
        if not user and 'user' in self.request.form:
            user = self.request.form['user']
        if not tag and 'tag' in self.request.form:
            tag = self.request.form['tag']
        if not path and 'path' in self.request.form:
            path = self.request.form['path']

        if not type_ and 'type' in self.request.form:
            type_ = self.request.form['type']
        if type_:
            if type_.lower() == 'event':
                type_ = 'plone.app.event.interfaces.IEvent'

        cat = getToolByName(self.context, 'portal_catalog')

        query = {}
        if type_:
            query['object_provides'] = type_
        else:
            query['object_provides'] = IBasetype.__identifier__

        query['sort_on'] = 'created'
        query['sort_order'] = 'reverse'

        if path:
            query['path'] = {'query': '/'.join(self.context.getPhysicalPath())}
        if user:
            query['Creator'] = user
        if tag:
            query['Subject'] = tag

        result = cat(batch=True, **query)
        return Batch(result, size=b_size, start=b_start)

    def element_provider(self, context):
        provider = getMultiAdapter((context, self.request, self),
                                   IContentProvider,
                                   name=u"element_provider")
        return provider.render()
