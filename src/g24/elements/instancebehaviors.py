from plone.behavior.interfaces import IBehavior
from plone.dexterity.behavior import DexterityBehaviorAssignable
from zope.annotation import IAnnotations
from zope.component import queryUtility
from zope.interface import alsoProvides, noLongerProvides
from g24.elements.config import INSTANCE_BEHAVIORS_KEY as KEY


class DexterityInstanceBehaviorAssignable(DexterityBehaviorAssignable):
    """ Support per instance specification of plone.behavior behaviors
    """

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


def enable_behaviors(obj, behaviors, ifaces):
    annotations = IAnnotations(obj)
    instance_behaviors = annotations.get(KEY, ())
    instance_behaviors += behaviors
    annotations[KEY] = instance_behaviors

    for iface in ifaces:
        alsoProvides(obj, iface)


def disable_behaviors(obj, behaviors, ifaces):
    annotations = IAnnotations(obj)
    instance_behaviors = annotations.get(KEY, ())
    instance_behaviors = filter(lambda x: x not in behaviors,
                                instance_behaviors)
    annotations[KEY] = instance_behaviors

    for iface in ifaces:
        noLongerProvides(obj, iface)
