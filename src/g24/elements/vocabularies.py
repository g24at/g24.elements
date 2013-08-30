from Products.CMFCore.utils import getToolByName
from zope.interface import directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from g24.elements.behaviors import IPlace


def Locations(context):
    cat = getToolByName(context, 'portal_catalog')
    query = {}
    query['object_provides'] = IPlace.__identifier__
    query['sort_on'] = 'sortable_title'
    items = [SimpleTerm(it.id, it.id, it.Title) for it in cat(**query)]
    return SimpleVocabulary(items)
directlyProvides(Locations, IVocabularyFactory)
