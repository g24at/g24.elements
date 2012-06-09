from zope.i18nmessageid import MessageFactory
packageName = __name__
messageFactory = MessageFactory(packageName)

def safe_decode(value):
    """ Return unicode object if value is a string.
    Otherwise, just return the value.

    >>> from g24.elements import safe_decode
    >>> safe_decode('bla')
    u'bla'
    >>> safe_decode(u'uhh')
    u'uhh'
    >>> safe_decode(123)
    123

    """
    if isinstance(value, str):
        return value.decode('utf-8')
    else:
        return value

def safe_encode(value):
    """ Return utf-8 encoded string if value is a unicode.
    Otherwise, just return the value.

    >>> from g24.elements import safe_encode
    >>> safe_encode('bla')
    'bla'
    >>> safe_encode(u'uhh')
    'uhh'
    >>> safe_encode(123)
    123

    """
    if isinstance(value, unicode):
        return value.encode('utf-8')
    else:
        return value
