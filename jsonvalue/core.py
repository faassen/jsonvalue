from pyld import jsonld
import json
from types import NoneType

# XXX skip @context dictionary when doing a dump/load

class JsonValue(object):
    def __init__(self):
        self._iri_to_value_type = {}
        self._iri_to_node_type = {}
        self._class_to_node_type = {}

    def value_type(self, iri, type):
        self._iri_to_value_type[iri] = type

    def node_type(self, iri, cls, type):
        self._iri_to_node_type[iri] = type
        # XXX use reg for this
        self._class_to_node_type[cls] = type

    def value_vocabulary(self, types):
        for iri, type in types.items():
            self.value_type(iri, type)

    def load_value(self, id, value, **kw):
        t = self._iri_to_value_type.get(id)
        if t is None or value is None:
            return value
        if not t.validate_load(value, **kw):
            raise ValueError("Cannot load value as %s: %r" %
                             (id, value))
        return t.load(value, **kw)

    def dump_value(self, id, value, **kw):
        t = self._iri_to_value_type.get(id)
        if t is None or value is None:
            return value
        if not t.validate_dump(value):
            raise ValueError("Cannot dump value as %s: %r" %
                             (id, value))
        return t.dump(value, **kw)

    def can_load_node(self, id, **kw):
        return id in self._iri_to_node_type

    def load_node(self, id, d, **kw):
        t = self._iri_to_node_type[id]
        return t.load(d, **kw)

    def can_dump_node(self, obj, **kw):
        return type(obj) in self._class_to_node_type

    def dump_node(self, obj, **kw):
        t = self._class_to_node_type[type(obj)]
        result = t.dump(obj, **kw)
        result['@type'] = t.id()
        return result

    def load_values(self, d, context=None):
        """Take JSON dict, return JSON dict with rich values.
        """
        original_context = d.get('@context')
        if context is None:
            context = original_context
        wrapped = {
            'http://jsonvalue.org/main': d,
            '@context': context
        }
        expanded = jsonld.expand(wrapped, dict(expandContext=context))
        wrapped_objects = LoadTransformer(
            self.load_node, self.can_load_node,
            self.load_value, context)(expanded)
        result = wrapped_objects['http://jsonvalue.org/main']
        if isinstance(result, dict) and original_context is not None:
            result['@context'] = original_context
        return result

    def dump_values(self, d, context=None):
        """Take rich JSON dict, return plain JSON dict without rich values.
        """
        if isinstance(d, dict):
            original_context = d.get('@context')
        else:
            original_context = None
        if context is None:
            context = original_context
        wrapped = {
            'http://jsonvalue.org/main': d,
            '@context': context
        }
        result = DumpTransformer(
            self.dump_node, self.can_dump_node, self.dump_value, context)(
                wrapped)
        wrapped_d = jsonld.compact(result, context)
        result = wrapped_d['http://jsonvalue.org/main']
        if isinstance(result, dict) and original_context is not None:
            result['@context'] = original_context
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
        self._cls = cls
        self.dump = dump
        self.load = load

    def id(self):
        return 'http://jsonvalue.org/internal/datatype/%s' % self._cls.__name__

    def validate_load(self, value):
        return True

    def validate_dump(self, value):
        return isinstance(value, self._cls)


class CustomNodeType(object):
    def __init__(self, cls, dump, load):
        self._cls = cls
        self.dump = dump
        self.load = load

    def id(self):
        return 'http://jsonvalue.org/internal/nodetype/%s' % self._cls.__name__

    def validate_load(self, value):
        if not isinstance(value, dict):
            return False
        type = value.get('@type')
        return type == self.id()

    def validate_dump(self, value):
        return isinstance(value, self._cls)


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


class LoadTransformer(object):
    def __init__(self, load_node, can_load_node, load_value, context):
        self.load_node = load_node
        self.can_load_node = can_load_node
        self.load_value = load_value
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
            d['@value'] = self.load_value(type, value)
            return d
        # XXX what if there are more than one node types?
        type = type[0]
        if not self.can_load_node(type):
            return d
        compacted = jsonld.compact(d, self.context)
        del compacted['@context']
        compacted = self.realize(compacted, objects)
        obj = self.load_node(type, compacted)
        if obj is None:
            return d
        new_id = 'http://jsonvalue.org/object/%s' % len(objects)
        objects[new_id] = obj
        return {
            '@type': 'http://jsonvalue.org/object_type',
            '@value': new_id,
        }


class DumpTransformer(object):
    def __init__(self, dump_node, can_dump_node, dump_value, context):
        self.dump_node = dump_node
        self.can_dump_node = can_dump_node
        self.dump_value = dump_value
        self.context = context

    def __call__(self, d):
        d = self.dump(d)
        expanded = jsonld.expand(d, dict(expandContext=self.context))
        return self._expanded(expanded)

    def dump(self, d):
        if isinstance(d, dict):
            return self._dump_dict(d)
        elif isinstance(d, list):
            return self._dump_list(d)
        elif isinstance(d, (basestring, int, float, bool, NoneType)):
            return d
        else:
            return self._dump_obj(d)

    def _dump_dict(self, d):
        result = {}
        for key, value in d.items():
            result[key] = self.dump(value)
        return result

    def _dump_list(self, l):
        return [self.dump(item) for item in l]

    def _dump_obj(self, obj):
        if not self.can_dump_node(obj):
            return obj
        return self.dump(self.dump_node(obj))

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
        d['@value'] = self.dump_value(type, value)
        return d
