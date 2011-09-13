# -*- coding: utf-8 -*-
"""Model wrapper for Google App Engine"""

from zope import schema
from zope.interface import implements

from pyramid.threadlocal import get_current_registry

from shaura_core.interfaces import IObject, IObjectManager
from shaura_gae.interfaces import IProperty

from google.appengine.ext import db


def createStringProperty(field):
    # FIXME: zope.schema fields are validated unbound
    return db.StringProperty(
        name=field.__name__, required=field.required,
        validator=field.validate)


def createEncodedStringProperty(field):
    # FIXME: zope.schema fields are validated unbound
    # WONTFIX: some zope.schema fields "require" encoded strings instead of
    # unicode strings, but GAE stores and returns all string properties as
    # unicode
    def encode(x):
        try:
            return x.encode("utf-8")
        except:
            return x
    return db.StringProperty(
        name=field.__name__, required=field.required,
        validator=lambda x: field.validate(encode(x)))


def createTextProperty(field):
    # FIXME: zope.schema fields are validated unbound
    return db.TextProperty(
        name=field.__name__, required=field.required,
        validator=field.validate)


def createDateTimeProperty(field):
    # FIXME: zope.schema fields are validated unbound
    return db.DateTimeProperty(
        name=field.__name__, required=field.required,
        validator=field.validate)


def createLinkProperty(field):
    # FIXME: zope.schema fields are validated unbound
    # WONTFIX: some zope.schema fields "require" encoded strings instead of
    # unicode strings, but GAE stores and returns all string properties as
    # unicode.
    def encode(x):
        try:
            return x.encode("utf-8")
        except:
            return x
    return db.LinkProperty(
        name=field.__name__, required=field.required,
        validator=lambda x: field.validate(encode(x)))


def createBooleanProperty(field):
    # FIXME: zope.schema fields are validated unbound
    return db.BooleanProperty(
        name=field.__name__, required=field.required,
        validator=field.validate)


def createListProperty(field):
    registry = get_current_registry()
    return registry.getMultiAdapter(
        (field, field.value_type), IProperty)


def createUnicodeListProperty(field, value_type):
    # FIXME: zope.schema fields are validated unbound
    return db.ListProperty(unicode, name=field.__name__,
                           validator=field.validate)


class SchemaPropertiedClass(db.PropertiedClass):
    """Meta-class for initializing model classes properties"""

    def __init__(cls, name, bases, dct, map_kind=True):
        """Initializes a class that might implement interfaces"""

        registry = get_current_registry()
        implements = getattr(cls, "__implements_advice_data__", None)
        for interface in (implements and implements[0] or ()):
            for name in schema.getFieldNamesInOrder(interface):
                field = interface[name]
                setattr(cls, name, registry.getAdapter(field, IProperty))
                dct.update({name: getattr(cls, name)})
        super(SchemaPropertiedClass, cls).__init__(name, bases, dct, map_kind)


class SchemaPropertiedModel(db.Model):
    """Meta class for models"""
    __metaclass__ = SchemaPropertiedClass


class Model(SchemaPropertiedModel):
    """Base class for models"""
    implements(IObject)


class ObjectManager(object):
    """Database access utility"""
    implements(IObjectManager)

    def __call__(self, **kwargs):
        kind = None
        try:
            kind = kwargs.pop("object_type")
        except KeyError:
            pass

        where = []
        values = []

        for key in kwargs:
            value = kwargs[key]
            if type(value) in (tuple, list):
                where.append("%s IN :%s" % (key, len(where) + 1))
                values.append(list(value))
            else:
                where.append("%s = :%s" % (key, len(where) + 1))
                values.append(value)

        if kind and where:
            query = db.GqlQuery("SELECT * FROM %s WHERE %s"
                                % (kind, " AND ".join(where)), *values)
        elif kind:
            query = db.GqlQuery("SELECT * FROM %s" % kind)
        else:
            query = db.GqlQuery()

        for result in query:
            yield result


def putCreatedObject(event):
    """Object created lifecycle event"""
    event.target.put()


def saveModifiedObject(event):
    """Object modified lifecycle event"""
    event.target.save()


def deleteObsoletedObject(event):
    """Object obsoleted lifecycle event"""
    event.target.delete()
