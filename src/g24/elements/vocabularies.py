from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from g24.elements.behaviors import IPlace


class LocationsVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context, query=None):
        cat = getToolByName(context, 'portal_catalog')
        query = {}
        query['object_provides'] = IPlace.__identifier__
        query['sort_on'] = 'sortable_title'
        items = [SimpleTerm(it.UID, title=it.Title) for it in cat(**query)]
        return SimpleVocabulary(items)

LocationsVocabularyFactory = LocationsVocabulary()
