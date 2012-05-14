from plone.app.event.dx.interfaces import (
    IDXEvent,
    IDXEventRecurrence,
    IDXEventLocation
)
from g24.elements.behaviors import (
    ITitle,
    IPlace        
)

INSTANCE_BEHAVIORS_KEY = 'g24.elements.instance_behaviors'

EVENT_INTERFACES = (IDXEvent, IDXEventRecurrence, IDXEventLocation)
EVENT_BEHAVIORS = ('plone.app.event.dx.behaviors.IEventBasic',
                   'plone.app.event.dx.behaviors.IEventRecurrence',
                   'plone.app.event.dx.behaviors.IEventLocation')

TITLE_INTERFACES =  (ITitle,)
TITLE_BEHAVIORS = ('g24.elements.behaviors.ITitle',)

PLACE_INTERFACES = (IPlace,)
PLACE_BEHAVIORS = ('g24.elements.behaviors.IPlace',)
