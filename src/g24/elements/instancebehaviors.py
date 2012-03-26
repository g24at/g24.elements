from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from zope.annotation import IAnnotations
from zope.interfaces import alsoProvides, noLongerProvides
from zope.component import adapts, queryUtility

from plone.behavior.interfaces import IBehavior
from plone.dexterity.behavior import DexterityBehaviorAssignable

from plone.app.event.dx.interfaces import (
    IDXEvent,
    IDXEventRecurrence,
    IDXEventLocation
)
from g24.elements.content import IBasetype
from g24.elements import INSTANCE_BEHAVIORS_KEY as KEY
from g24.elements import messageFactory as _

EVENT_BEHAVIORS = ('plone.app.event.dx.behaviors.IEventBasic',
                   'plone.app.event.dx.behaviors.IEventRecurrence',
                   'plone.app.event.dx.behaviors.IEventLocation')

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

    def __call__(self):
        context = aq_inner(self.context)
        annotations = IAnnotations(context)
        instance_behaviors = annotations.get(KEY, ())
        instance_behaviors += EVENT_BEHAVIORS
        annotations[KEY] = instance_behaviors

        alsoProvides(context, IDXEvent, IDXEventRecurrence, IDXEventLocation)

        IStatusMessage(self.request).add(
            _(u"Event behavior is enabled for this content."), u"info")
        return self.request.RESPONSE.redirect('%s/edit' %
                    '/'.join(context.getPhysicalPath()))

class DisableEvent(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        annotations = IAnnotations(context)
        instance_behaviors = annotations.get(KEY, ())
        instance_behaviors = filter(lambda x: x not in EVENT_BEHAVIORS,
                                    instance_behaviors)
        annotations[KEY] = instance_behaviors

        noLongerProvides(context, IDXEvent)
        noLongerProvides(context, IDXEventRecurrence)
        noLongerProvides(context, IDXEventLocation)

        IStatusMessage(self.request).add(
            _(u"Event behavior is disabled for this content."), u"info")
        return self.request.RESPONSE.redirect(
                '/'.join(context.getPhysicalPath()))
