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

    def load_value(self, id, value):
        type = self._url_to_type.get(id)
        if type is None or value is None:
            return value
        if not type.validate_load(value):
            raise ValueError("Cannot load as %s: %r" %
                             (type.id(), value))
        return type.load(value)

    def dump_value(self, id, value):
        type = self._url_to_type.get(id)
        if type is None or value is None:
            return value
        if not type.validate_dump(value):
            raise ValueError("Cannot dump as %s: %r" %
                             (type.id(), value))
        return type.dump(value)

    def to_values(self, d, context=None):
        """Take JSON dict, return JSON dict with rich values.
        """
        original_context = d.get('@context')
        if context is None:
            context = original_context
        expanded = self.expand_to_values(d, context)
#        objectified = self.objectify(expanded, context)
        result = jsonld.compact(expanded, context)
        if original_context is None:
            del result['@context']
        return result

    def from_values(self, d, context=None):
        """Take rich JSON dict, return plain JSON dict without rich values.
        """
        original_context = d.get('@context')
        if context is None:
            context = original_context
        result = self.compact_from_values(
            jsonld.expand(d, dict(expandContext=context)),
            context)
        if original_context is None:
            del result['@context']
        return result

    # def objectify(self, l, context):
        
    #     # XXX need to use context to expand type
    #     type = d.get('@type')
    #     # XXX type being array
    #     if type is not None:
    #         return self.load_value(d)
    #     result = {}
        
    #     for key, value in d.items():
    #         if 
    def expand_to_values(self, d, context):
        """Take JSON dict, return expanded dict with rich values.
        """
        return _transform_expanded(
            jsonld.expand(d,dict(expandContext=context)),
            self.load_value)

    def compact_from_values(self, expanded, context):
        """Take expanded JSON list, return JSON dict with plain values.
        """
        return jsonld.compact(_transform_expanded(expanded, self.dump_value),
                              context)


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


def _transform_expanded(expanded, transform):
    result = []
    for d in expanded:
        result.append(_transform_dict(d, transform))
    return result


def _transform_dict(d, transform):
    result = {}
    for key, l in d.items():
        if not isinstance(l, list):
            result[key] = l
            continue
        result[key] = _transform_list(l, transform)
    return result


def _transform_list(l, transform):
    result = []
    for d in l:
        if not isinstance(d, dict):
            result.append(d)
            continue
        result.append(_transform_value(d, transform))
    return result


def _transform_value(d, transform):
    type = d.get('@type')
    if type is None:
        return _transform_dict(d, transform)
    value = d.get('@value')
    if value is None:
        return _transform_dict(d, transform)
    d = d.copy()
    d['@value'] = transform(type, value)
    return d


def _objectify_expanded(expanded, transform):
    result = []
    for d in expanded:
        result.append(_objectify_dict(d, transform))
    return result


def _objectify_dict(d, transform):
    result = {}
    for key, l in d.items():
        if not isinstance(l, list):
            result[key] = l
            continue
        result[key] = _objectify_list(l, transform)
    return result


def _objectify_list(l, transform):
    result = []
    for d in l:
        if not isinstance(d, dict):
            result.append(d)
        result.append(_objectify_value(d, transform))
    return result


def _objectify_value(d, transform):
    type = d.get('@type')
    if type is None:
        return d
    value = d.get('@value')
    if value is None:
        return d
    d = d.copy()
    d['@value'] = transform(type, value)
    return d
