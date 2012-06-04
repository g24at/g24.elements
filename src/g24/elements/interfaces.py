from zope.interface import Interface
from plone.directives import form

class IG24ElementsLayer(Interface):
    """ g24 elements theme layer.
    """

class IBasetypeAccessor(Interface):
    """ Get/set accessor for IBasetype instances.
    """

class IBasetype(form.Schema):
    """ g24.elements Basetype content.
    """
