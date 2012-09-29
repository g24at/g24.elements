from Products.CMFCore.utils import getToolByName
from plone.batching import Batch
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider

from g24.elements import safe_decode
from g24.elements.interfaces import IBasetype
from g24.elements.behaviors import IPlace, IThread
from plone.event.interfaces import IEvent

class StreamView(BrowserView):

    def items(self, user=None, tag=None, in_path=False, type_=None):

        # batch paging
        b_start = 'b_start' in self.request.form and int(self.request.form['b_start']) or 0
        b_size = 10

        # filter
        if not user and 'user' in self.request.form:
            user = safe_decode(self.request.form['user'])
        if not tag and 'tag' in self.request.form:
            tag = safe_decode(self.request.form['tag'])
        if not in_path and 'in_path' in self.request.form:
            in_path = self.request.form['in_path']

        if not type_ and 'type' in self.request.form:
            type_ = self.request.form['type']
        if type_:
            ty = type_.lower()
            if ty == 'event':
                type_ = IEvent.__identifier__
            elif ty == 'thread':
                type_ = IThread.__identifier__
            elif ty == 'place':
                type_ = IPlace.__identifier__
            else:
                type_= None
        else:
            # if no other type is given, search for IBasetype
            type_ = IBasetype.__identifier__

        query = {}

        query['object_provides'] = type_
        query['sort_on'] = 'created'
        query['sort_order'] = 'reverse'

        if in_path:
            query['path'] = {'query': '/'.join(self.context.getPhysicalPath())}
        if user:
            query['Creator'] = user
        if tag:
            query['Subject'] = tag

        cat = getToolByName(self.context, 'portal_catalog')
        result = cat(batch=True, **query)
        return Batch(result, size=b_size, start=b_start)

    def element_provider(self, context):
        provider = getMultiAdapter((context, self.request, self),
                                   IContentProvider,
                                   name=u"element_provider")
        return provider.render()
