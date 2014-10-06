from pyld import jsonld
import json


class JsonValue(object):
    def __init__(self):
        self._url_to_type = {}

    def type(self, iri, type):
        self._url_to_type[iri] = type

    def vocabulary(self, types):
        for type in types:
            self.type(type.id(), type)

    def load_value(self, id, value, **kw):
        type = self._url_to_type.get(id)
        if type is None or value is None:
            return value
        if not type.validate_load(value, **kw):
            raise ValueError("Cannot load as %s: %r" %
                             (type.id(), value))
        return type.load(value, **kw)

    def dump_value(self, id, value, **kw):
        type = self._url_to_type.get(id)
        if type is None or value is None:
            return value
        if not type.validate_dump(value):
            raise ValueError("Cannot dump as %s: %r" %
                             (type.id(), value))
        return type.dump(value, **kw)

    def to_values(self, d, context=None):
        """Take JSON dict, return JSON dict with rich values.
        """
        original_context = d.get('@context')
        if context is None:
            context = original_context
        wrapped = { 'http://jsonvalue.org/main': d,
                    '@context': context }
        expanded = jsonld.expand(wrapped, dict(expandContext=context))
        wrapped_objects = ToValuesTransformer(
            self.load_value, context)(expanded)
        result = wrapped_objects['http://jsonvalue.org/main']
        if isinstance(result, dict) and original_context is not None:
            result['@context'] = original_context
        return result

    def from_values(self, d, context=None):
        """Take rich JSON dict, return plain JSON dict without rich values.
        """
        original_context = d.get('@context')
        if context is None:
            context = original_context
        expanded = jsonld.expand(d, dict(expandContext=context))
        result = FromValuesTransformer(
            self.dump_value, self.dump_value, context)(expanded)
        result = jsonld.compact(result, context)
        if original_context is None:
            del result['@context']
        return result

    # JSON module style API
    def dump(self, obj, *args, **kw):
        return json.dump(self.from_values(obj, kw.pop('context', None)),
                         *args, **kw)

    def dumps(self, obj, *args, **kw):
        return json.dumps(self.from_values(obj, kw.pop('context', None)),
                          *args, **kw)

    def load(self, *args, **kw):
        context = kw.pop('context', None)
        plain = json.load(*args, **kw)
        return self.to_values(plain, context)

    def loads(self, *args, **kw):
        context = kw.pop('context', None)
        plain = json.loads(*args, **kw)
        return self.to_values(plain, context)


class CustomDataType(object):
    def __init__(self, cls, dump, load):
        self.cls = cls
        self.dump = dump
        self.load = load

    def id(self):
        return 'http://jsonvalue.org/internal/datatype/%s' % self.cls.__name__

    def validate_load(self, value):
        return True

    def validate_dump(self, value):
        return isinstance(value, self.cls)


class CustomNodeType(object):
    def __init__(self, cls, dump, load):
        self.cls = cls
        self.dump = dump
        self.load = load

    def id(self):
        return 'http://jsonvalue.org/internal/nodetype/%s' % self.cls.__name__

    def validate_load(self, value):
        if not isinstance(value, dict):
            return False
        type = value.get('@type')
        return type == self.id()

    def validate_dump(self, value):
        return isinstance(value, self.cls)


def datatypes(d):
    """Convenience way to specify context using datatype designators.
    """
    context = {}
    for term, datatype in d.items():
        if isinstance(datatype, basestring):
            type_id = datatype
        else:
            type_id = datatype.id()
        # XXX can we use some better IRI for this?
        id = 'http://jsonvalue.org/internal/id/%s' % term
        context[term] = {
            '@id': id,
            '@type': type_id,
        }
    return context


class ToValuesTransformer(object):
    def __init__(self, transform, context):
        self.transform = transform
        self.context = context

    def __call__(self, expanded):
        objects = {}
        objectified = self._list(expanded, objects)
        compacted = jsonld.compact(objectified, self.context)
        return self.realize(compacted, objects)

    def realize(self, o, objects):
        if isinstance(o, dict):
            return self._realize_dict(o, objects)
        elif isinstance(o, list):
            return self._realize_list(o, objects)
        else:
            return o

    def _realize_dict(self, d, objects):
        type = d.get('@type')
        if type == 'http://jsonvalue.org/object_type':
            value = d.get('@value')
            return objects[value]
        result = {}
        for key, value in d.items():
            result[key] = self.realize(value, objects)
        return result

    def _realize_list(self, l, objects):
        return [self.realize(value, objects) for value in l]

    def _expanded(self, expanded, objects):
        result = []
        for d in expanded:
            result.append(self._dict(d, objects))
        return result

    def _dict(self, d, objects):
        result = {}
        for key, l in d.items():
            if not isinstance(l, list):
                result[key] = l
                continue
            result[key] = self._list(l, objects)
        return result

    def _list(self, l, objects):
        result = []
        for d in l:
            if not isinstance(d, dict):
                result.append(d)
                continue
            result.append(self._value(d, objects))
        return result

    def _value(self, d, objects):
        d = self._dict(d, objects)
        type = d.get('@type')
        if type is None:
            return d
        value = d.get('@value')
        if value is not None:
            d = d.copy()
            d['@value'] = self.transform(type, value)
            return d
        # XXX what if there are more than one node types?
        type = type[0]
        # XXX would be nice to be able to avoid compaction if
        # type isn't recognized anyway. either move this logic
        # into transform somehow (but how to get context and objects?)
        # or extend transformation api with can_transform
        compacted = jsonld.compact(d, self.context)
        del compacted['@context']
        compacted = self.realize(compacted, objects)
        obj = self.transform(type, compacted)
        if obj is None:
            return d
        new_id = 'http://jsonvalue.org/object/%s' % len(objects)
        objects[new_id] = obj
        return {
            '@type': 'http://jsonvalue.org/object_type',
            '@value': new_id,
        }


class FromValuesTransformer(object):
    def __init__(self, transform_node, transform_value, context):
        self.transform_node = transform_node
        self.transform_value = transform_value
        self.context = context

    def __call__(self, expanded):
        return self._expanded(expanded)

    def _expanded(self, expanded):
        result = []
        for d in expanded:
            result.append(self._dict(d))
        return result

    def _dict(self, d):
        result = {}
        for key, l in d.items():
            if not isinstance(l, list):
                result[key] = l
                continue
            result[key] = self._list(l)
        return result

    def _list(self, l):
        result = []
        for d in l:
            if not isinstance(d, dict):
                result.append(d)
                continue
            result.append(self._value(d))
        return result

    def _value(self, d):
        type = d.get('@type')
        if type is None:
            return self._dict(d)
        value = d.get('@value')
        if value is None:
            return self._dict(d)
        d = d.copy()
        d['@value'] = self.transform_value(type, value)
        return d
