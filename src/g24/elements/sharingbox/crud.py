from Acquisition import aq_inner, aq_base
from Acquisition.interfaces import IAcquirer
from g24.elements.interfaces import IBasetypeAccessor
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import addContentToContainer
from zope.component import getUtility, createObject
from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent


def create(context, type_):
    """ Create element, set attributes and add it to container.
    """
    fti = getUtility(IDexterityFTI, name=type_)

    container = aq_inner(context)
    obj = createObject(fti.factory)

    # Note: The factory may have done this already, but we want to be sure
    # that the created type has the right portal type. It is possible
    # to re-define a type through the web that uses the factory from an
    # existing type, but wants a unique portal_type!

    if hasattr(obj, '_setPortalTypeName'):
        obj._setPortalTypeName(fti.getId())

    # Acquisition wrap temporarily to satisfy things like vocabularies
    # depending on tools
    if IAcquirer.providedBy(obj):
        obj = obj.__of__(container)

    obj = aq_base(obj)
    if obj:
        notify(ObjectCreatedEvent(obj))
    return obj


def add(obj, container):
    # add
    container = aq_inner(container)
    obj = addContentToContainer(container, obj)
    if obj:
        notify(ObjectAddedEvent(obj))
    return obj


def edit(obj, data, order=[], ignores=[]):
    """Edit the attributes of an object.

    :param data:    Flat data structure:   {fieldname: value}
    :type data: dict

    :param order:   Optional list of attribute names to be set in the defined
                    order. If a attribute defined in order isn't found in data,
                    it is deleted from the object.
    :type order: list

    :param ignores: Optional list of attribute names to be ignored.
    :type ignores: list
    """

    # access content via an accessor, respecting the behaviors
    accessor = IBasetypeAccessor(obj)

    # first set attributes in the order as defined in order
    for attr in order:
        if attr in data:
            setattr(accessor, attr, data[attr])
        elif hasattr(accessor, attr):  # attr not in data
            delattr(accessor, attr)

    # then set all other
    for key, val in data.iteritems():
        if key in order or key in ignores:
            continue
        setattr(accessor, key, val)

    notify(ObjectModifiedEvent(obj))
    obj.reindexObject()  # TODO: does notify ObjectModifiedEvent start this?
