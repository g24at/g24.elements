import json
import pytz
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from plone.app.vocabularies.catalog import KeywordsVocabulary
from g24.elements.behaviors import IPlace


class VocabulariesView(BrowserView):

    def __call__(self):
        # does nothin', if called directly
        return None
    
    # vocabularies

    # TODO: cache/memoize
    @property
    def vocabulary_keywords(self):
        vocab = KeywordsVocabulary()
        result = vocab(self.context)
        return [it.title for it in result]

    @property
    def vocabulary_locations(self):
        cat = getToolByName(self.context, 'portal_catalog')
        query = {}
        query['object_provides'] = IPlace.__identifier__
        query['sort_on'] = 'sortable_title'
        return [(it.id, it.Title) for it in cat(**query)]

    @property
    def vocabulary_timezones(self):
        return pytz.all_timezones


    def _json_vocab(self, items, tuples=False):
        """ Return a json string from a list filtered by a query string.

        """
        req = self.request
        req.response.setHeader("Content-type", "application/json")
        query = None
        if 'q' in req.form:
            # filter by query string in tag's title.
            # for better matching, all lower cased.
            query = req.form['q']

        # apply filter
        if tuples and query:
            items = filter(lambda it: query.lower() in it[1].lower(), items)
        elif query:
            items = filter(lambda it: query.lower() in it.lower(), items)

        # map items into datastructure
        if tuples:
            item_map = map(lambda it: dict(v=it[0], n=it[1]), items)
        else:
            item_map = map(lambda it: dict(v=it), items)

        json_string = json.dumps(item_map)
        return json_string


    # additional browser page methods

    def query_tags(self):
        """ Return a json string with tags filtered by a query string.

        """
        return self._json_vocab(self.vocabulary_keywords)

    def query_locations(self):
        """ Return a json string with locations filtered by a query string.

        """
        return self._json_vocab(self.vocabulary_locations, tuples=True)

    def query_timezones(self):
        """ Return a json string with timezones filtered by a query string.

        """
        return self._json_vocab(self.vocabulary_timezones)
