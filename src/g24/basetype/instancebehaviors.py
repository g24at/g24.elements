from zope.annotation import IAnnotations
from zope.component import adapts, queryUtility

from plone.behavior.interfaces import IBehavior
from plone.dexterity.behavior import DexterityBehaviorAssignable

from g24.basetype.interfaces import IBaseType
from g24.basetype.config import INSTANCE_BEHAVIORS_KEY as KEY

class DexterityInstanceBehaviorAssignable(DexterityBehaviorAssignable):
    """ Support per instance specification of plone.behavior behaviors
    """
    adapts(IBaseType)

    def __init__(self, context):
        super(DexterityInstanceBehaviorAssignable, self).__init__(context)
        annotations = IAnnotations(context)
        self.instance_behaviors = annotations.get(KEY, ())

    def enumerateBehaviors(self):
        self.behaviors = self.fti.behaviors + self.instance_behaviors
        for name in self.behaviors:
            behavior = queryUtility(IBehavior, name=name)
            if behavior is not None:
                yield behavior
