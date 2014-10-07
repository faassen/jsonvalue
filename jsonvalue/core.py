from pyld import jsonld
import json
from types import NoneType

from .error import ValueLoadError, LoadError, ValueDumpError, DumpError


class JsonValue(object):
    def __init__(self):
        self._iri_to_value_type = {}
        self._iri_to_node_type = {}
        self._class_to_node_type = {}

    def value_type(self, iri, type):
        self._iri_to_value_type[iri] = type

    def node_type(self, iri, type):
        self._iri_to_node_type[iri] = type
        # XXX use reg for this
        self._class_to_node_type[type.cls] = type

    def value_vocabulary(self, types):
        for iri, type in types.items():
            self.value_type(iri, type)

    def load_value(self, term, type, value, **kw):
        t = self._iri_to_value_type.get(type)
        if t is None or value is None:
            return value
        if not t.validate_load(value, **kw):
            raise ValueLoadError(term, type, value)
        try:
            return t.load(value, **kw)
        except ValueError:
            raise ValueLoadError(term, type, value)

    def load_context(self, type):
        return self._iri_to_node_type[type].load_context

    def dump_value(self, term, type, value, **kw):
        t = self._iri_to_value_type.get(type)
        if t is None or value is None:
            return value
        if not t.validate_dump(value):
            raise ValueDumpError(term, type, value)
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

    def load_objects(self, d, context=None):
        """Take JSON dict, return rich values.
        """
        original_context = d.get('@context')
        if context is None:
            context = original_context
        wrapped = {
            'http://jsonvalue.org/main': d,
            '@context': context
        }
        expanded = jsonld.expand(wrapped, dict(expandContext=context))
        wrapped_objects = LoadTransformer(self, context)(expanded)
        result = wrapped_objects['http://jsonvalue.org/main']
        if isinstance(result, dict) and original_context is not None:
            result['@context'] = original_context
        return result

    def dump_objects(self, d, context=None):
        """Take objects, return plain JSON dict without rich values.
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
        return json.dump(self.dump_objects(obj, kw.pop('context', None)),
                         *args, **kw)

    def dumps(self, obj, *args, **kw):
        return json.dumps(self.dump_objects(obj, kw.pop('context', None)),
                          *args, **kw)

    def load(self, *args, **kw):
        context = kw.pop('context', None)
        plain = json.load(*args, **kw)
        return self.load_objects(plain, context)

    def loads(self, *args, **kw):
        context = kw.pop('context', None)
        plain = json.loads(*args, **kw)
        return self.load_objects(plain, context)


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
    def __init__(self, cls, dump, load, load_context):
        self.cls = cls
        self.dump = dump
        self.load = load
        self.load_context = load_context

    def id(self):
        return 'http://jsonvalue.org/internal/nodetype/%s' % self.cls.__name__

    def validate_load(self, value):
        if not isinstance(value, dict):
            return False
        type = value.get('@type')
        return type == self.id()

    def validate_dump(self, value):
        return isinstance(value, self.cls)


def valuetypes(d):
    """Convenience way to specify context using value type designators.
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


class LoadInfo(object):
    def __init__(self):
        self.objects = {}
        self.errors = []


class LoadTransformer(object):
    def __init__(self, jv, context):
        self.jv = jv
        self.context = context

    def __call__(self, expanded):
        load_info = LoadInfo()
        objectified = self._list('_', expanded, load_info)
        if load_info.errors:
            # for a stable errors listing
            load_info.errors.sort(key=lambda err: err.term)
            raise LoadError(load_info.errors)
        compacted = jsonld.compact(objectified, self.context)
        return self.realize(compacted, load_info.objects)

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

    def _dict(self, d, info):
        result = {}
        for term, l in d.items():
            if not isinstance(l, list):
                result[term] = l
                continue
            result[term] = self._list(term, l, info)
        return result

    def _list(self, term, l, info):
        result = []
        for d in l:
            if not isinstance(d, dict):
                result.append(d)
                continue
            result.append(self._value(term, d, info))
        return result

    def _value(self, term, d, info):
        d = self._dict(d, info)
        type = d.get('@type')
        if type is None:
            return d
        value = d.get('@value')
        if value is not None:
            d = d.copy()
            try:
                d['@value'] = self.jv.load_value(term, type, value)
            except ValueLoadError, e:
                info.errors.append(e)
            return d
        # XXX what if there are more than one node types?
        type = type[0]
        if not self.jv.can_load_node(type):
            return d
        load_context = self.jv.load_context(type)
        compacted = jsonld.compact(d, load_context)
        del compacted['@context']
        compacted = self.realize(compacted, info.objects)
        obj = self.jv.load_node(type, compacted)
        if obj is None:
            return d
        new_id = 'http://jsonvalue.org/object/%s' % len(info.objects)
        info.objects[new_id] = obj
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
        errors = []
        result = self._expanded(expanded, errors)
        if errors:
            # for a stable errors listing
            errors.sort(key=lambda err: err.term)
            raise DumpError(errors)
        return result

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
            if key.startswith('@'):
                result[key] = value
                continue
            result[key] = self.dump(value)
        return result

    def _dump_list(self, l):
        return [self.dump(item) for item in l]

    def _dump_obj(self, obj):
        if not self.can_dump_node(obj):
            return obj
        return self.dump(self.dump_node(obj))

    # XXX get rid of it and use _list always?
    def _expanded(self, expanded, errors):
        result = []
        for d in expanded:
            result.append(self._dict(d, errors))
        return result

    def _dict(self, d, errors):
        result = {}
        for term, l in d.items():
            if not isinstance(l, list):
                result[term] = l
                continue
            result[term] = self._list(term, l, errors)
        return result

    def _list(self, term, l, errors):
        result = []
        for d in l:
            if not isinstance(d, dict):
                result.append(d)
                continue
            result.append(self._value(term, d, errors))
        return result

    def _value(self, term, d, errors):
        type = d.get('@type')
        if type is None:
            return self._dict(d, errors)
        value = d.get('@value')
        if value is None:
            return self._dict(d, errors)
        d = d.copy()
        try:
            d['@value'] = self.dump_value(term, type, value)
        except ValueDumpError, e:
            errors.append(e)
        return d
