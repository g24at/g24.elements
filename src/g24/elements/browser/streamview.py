from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from g24.elements.content import IBasetype

class StreamView(BrowserView):

    def items(self):
        # TODO: get parameters from request or pass as arguments
        
        cat = getToolByName(self.context, 'portal_catalog')

        query = {}
        query['object_provides'] = IBasetype.__identifier__

        query['sort_on'] = 'created'
        query['sort_order'] = 'reverse'

        result = cat(**query)
        return result
