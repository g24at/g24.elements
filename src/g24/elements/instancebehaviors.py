from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from zope.annotation import IAnnotations
from zope.component import adapts, queryUtility

from plone.behavior.interfaces import IBehavior
from plone.dexterity.behavior import DexterityBehaviorAssignable

from g24.elements.content import IBasetype
from g24.elements import INSTANCE_BEHAVIORS_KEY as KEY
from g24.elements import messageFactory as _

class DexterityInstanceBehaviorAssignable(DexterityBehaviorAssignable):
    """ Support per instance specification of plone.behavior behaviors
    """
    adapts(IBasetype)

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


class EnableEvent(BrowserView):

    def render(self):
        context = aq_inner(self.context)
        annotations = IAnnotations(context)
        instance_behaviors = annotations.get(KEY, ())
        instance_behaviors += ('plone.app.event.dx.behaviors.IEventBasic',
                               'plone.app.event.dx.behaviors.IEventRecurrence',
                               'plone.app.event.dx.behaviors.IEventLocation',)
        annotations[KEY] = instance_behaviors

        IStatusMessage(self.request).add(
            _(u"Event behavior is enabled for this content."), u"info")
        return self.request.RESPONSE.redirect(
                    '/'.join(context.getPhysicalPath()))
