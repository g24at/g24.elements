from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.container.interfaces import INameChooser
from zope.interface import implements
import transaction


class ElementIdChooser(object):
    """A name chooser for a G24 elements.
    """
    implements(INameChooser)

    def __init__(self, context):
        self.context = context

    def checkName(self, name, object):
        context = aq_inner(self.context)
        cat = getToolByName(context, 'portal_catalog')
        res = cat.searchResults(id=name)
        if res:
            raise ValueError("Name not unique.")
        else:
            return True

    def chooseName(self, name, object):
        # get/set maxid
        site = getSite()
        g24element_max_id = getattr(site, 'g24element_max_id', None)
        if g24element_max_id is None:
            g24element_max_id = site.g24element_max_id = 1
        else:
            g24element_max_id += 1
            site.g24element_max_id = g24element_max_id
            transaction.get().commit()  # TODO: thread safety?
            #transaction.commit(1) # subtransaction commit

        return str(g24element_max_id)
