from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from g24.elements.content import IBasetype

class StreamView(BrowserView):

    def items(self, user=None, tag=None):
        # TODO: get parameters from request or pass as arguments
        #

        if not user and 'user' in self.request.form:
            user = self.request.form['user']
        if not tag and 'tag' in self.request.form:
            tag = self.request.form['tag']

        cat = getToolByName(self.context, 'portal_catalog')

        query = {}
        query['object_provides'] = IBasetype.__identifier__

        query['sort_on'] = 'created'
        query['sort_order'] = 'reverse'

        if user:
            query['Creator'] = user
        if tag:
            query['Subject'] = tag

        result = cat(**query)

        return result
