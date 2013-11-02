from Products.CMFCore.utils import getToolByName
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from g24.elements.behaviors import IPlace
from zope.interface import directlyProvides
from Products.CMFPlone.utils import safe_unicode
from zope.component.hooks import getSite


def LocationsVocabulary(context, query=None):
    """Vocabulary factory for countries regarding to ISO3166.
    """
    cat = getToolByName(getSite(), 'portal_catalog')
    cat_query = {}
    cat_query['object_provides'] = IPlace.__identifier__
    cat_query['sort_on'] = 'sortable_title'
    items = [SimpleTerm(value=it.UID, title=safe_unicode(it.Title))
             for it in cat(**cat_query)
             if query is None
             or safe_unicode(query).lower() in safe_unicode(it.Title).lower()]
    return SimpleVocabulary(items)
directlyProvides(LocationsVocabulary, IVocabularyFactory)
