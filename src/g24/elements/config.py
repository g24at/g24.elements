from plone.app.event.dx.interfaces import (
    IDXEvent,
    IDXEventRecurrence,
    IDXEventLocation
)

INSTANCE_BEHAVIORS_KEY = 'g24.elements.instance_behaviors'

EVENT_INTERFACES = (IDXEvent, IDXEventRecurrence, IDXEventLocation)
EVENT_BEHAVIORS = ('plone.app.event.dx.behaviors.IEventBasic',
                   'plone.app.event.dx.behaviors.IEventRecurrence',
                   'plone.app.event.dx.behaviors.IEventLocation')
