from Products.CMFCore.utils import getToolByName
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from g24.elements.behaviors import IPlace
from zope.interface import directlyProvides
from Products.CMFPlone.utils import safe_unicode


def LocationsVocabulary(context):
    """Vocabulary factory for countries regarding to ISO3166.
    """
    cat = getToolByName(context, 'portal_catalog')
    query = {}
    query['object_provides'] = IPlace.__identifier__
    query['sort_on'] = 'sortable_title'
    items = [SimpleTerm(value=it.UID, title=safe_unicode(it.Title))
             for it in cat(**query)]
    return SimpleVocabulary(items)
directlyProvides(LocationsVocabulary, IVocabularyFactory)
