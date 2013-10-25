from g24.elements.interfaces import ISchemaSerializer
from g24.elements.interfaces import IBasetype
from plone.formwidget.geolocation.field import GeolocationField

from plone.dexterity.utils import iterSchemata
from zope.schema import getFieldsInOrder

from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.supermodel.utils import mergedTaggedValueDict
import AccessControl.Permissions
from AccessControl import getSecurityManager
from zope.component import queryUtility
from zope.security.interfaces import IPermission

from Products.Five.browser import BrowserView
from plone.namedfile.file import NamedBlobImage
from datetime import date, datetime
import json
from zope.component import adapts
from zope.interface import implements


class SchemaSerializer(object):
    """SchemaSerializer taken from:
    https://github.com/eleddy/plone.dexterity/
        blob/master/plone/dexterity/content.py
    """
    adapts(IBasetype)
    implements(ISchemaSerializer)

    def __init__(self, content):
        self.content = content

    def getField(self, name):
        """Given a field name, return a field instance. Party hard.
        """
        fields = self.getFields()
        for field in fields:
            if field.getName() == name:
                return field
        return None

    def getFields(self):
        """Return all fields for this content type, as field instances.
        Because of behaviors, fields are distributed across several
        schemata. Fields will be returned in proper order.
        """
        fields = []
        for schemata in iterSchemata(self.content):
            fieldsInOrder = getFieldsInOrder(schemata)
            # TODO: once python 2.6 support is out, make this an OrderedDict
            for orderedField in fieldsInOrder:
                fields.append(orderedField[-1])
        return fields

    def getFieldNames(self):
        """Return a list of the names of the fields. Just some convenience
        cause I love yo faces!
        """
        return self.asDictionary().keys()

    def asDictionary(self, checkConstraints=False):
        """Return a dictionary of key, value pairs of all fields.
        If checkContraints is True, it will onyl return values
        that the authenticated user is allowed to see. Otherwise,
        all attribute,value pairs are returned.
        """
        hotness = {}  # pep8
        fields = self.getFields()
        for field in fields:
            if checkConstraints:
                if not self.canViewField(field):
                    continue
            val = self.getValue(field)
            if val is None:
                continue
            if isinstance(field, GeolocationField):
                # TODO: HACK!
                # TODO: should GeolocationField changed, so that it doesn't
                #       return another object?
                hotness['latitude'] = val.latitude
                hotness['longitude'] = val.longitude
            else:
                hotness[field.getName()] = val
        return hotness

    def canViewField(self, field):
        """returns True if the logged in user has permission to view this
        field
        """
        info = mergedTaggedValueDict(field.interface, READ_PERMISSIONS_KEY)

        # If there is no specific read permission, assume it is view
        if field not in info:
            gsm = getSecurityManager()
            perm = AccessControl.Permissions.view
            return gsm.checkPermission(perm, self.content)

        permission = queryUtility(IPermission, name=info[field])
        if permission is not None:
            return getSecurityManager().checkPermission(permission.title, self)

        return False

    def getValue(self, field):
        """While it may seem like you should just be able to access
        this contents attributes, this is not true :|. If something
        is provided as an adapter the adapter must be applied to get
        the actual field value. We can't use get() because Container
        overrides it to get subitems. So we use this obscure interface
        syntax instead of looking up and adapting the schema.

        Begin face exploding sequence in 3,2,1...
        """
        behaviorAdapter = field.interface(self.content)
        return getattr(behaviorAdapter, field.getName(), None)


class JsonView(BrowserView):
    """Serialize a Dexterity content type to JSON
    Taken from:
    https://raw.github.com/eleddy/puget.batshitcrazy/master/puget/
        batshitcrazy/browser/serialize.py
    """
    def __call__(self):
        item = self.context
        meta = {
            'type': item.portal_type,
            'id': item.id,
            # ??? allow this section to be turned off
            'creator': item.Creator(),
            'created': str(item.creation_date),
            'url': item.absolute_url(),
            # DateTime is not JSON serializable
            'modfied': str(item.modification_date),
        }
        ser = ISchemaSerializer(item)
        fields = ser.asDictionary(checkConstraints=True)
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        marshall = {
            'meta': meta,
            'fields': fields,
        }
        return json.dumps(marshall, cls=IsoDateTimeEncoder)

from g24.elements.browser.streamview import StreamView
from g24.elements.interfaces import IBasetypeAccessor
class GeoJsonView(StreamView):

    def __call__(self):
        items = self.items(type_='place')

        # 200 items at most

        def _make_feature(acc):
            feature = {
                "type": "Feature",
                "properties": {
                    "title": acc.title,
                    "uuid": acc.uid,
                    "link": acc.url
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        acc.longitude,
                        acc.latitude
                    ]
                }
            }
            return feature

        features = []
        for item in items:
            acc = IBasetypeAccessor(item.getObject())
            if acc.latitude and acc.longitude:
                features.append(_make_feature(acc))

        feature_collection = None
        if features:
            feature_collection = {
                "type": "FeatureCollection",
                "features": features
            }

        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        return json.dumps(feature_collection)


class IsoDateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime) or isinstance(obj, date):
            # standard JSON time format
            return obj.isoformat()
        elif isinstance(obj, NamedBlobImage):
            # ideally this actually resturns url but given that the
            # caller alerady has context, they can do it for now
            return obj.filename

        return json.JSONEncoder.default(self, obj)
