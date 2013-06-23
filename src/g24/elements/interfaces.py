from zope.interface import Interface
from plone.supermodel import model


class IG24ElementsLayer(Interface):
    """ g24 elements theme layer.
    """

class IBasetypeAccessor(Interface):
    """ Get/set accessor for IBasetype instances.
    """

class IBasetype(model.Schema):
    """ g24.elements Basetype content.
    """

class IBasetypeContainer(model.Schema):
    """ g24.elements Basetype content.
    """

class ISharingbox(model.Schema):
    """Sharingbo marker interface."""
