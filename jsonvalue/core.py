from pyld import jsonld
import json


class JsonValue(object):
    def __init__(self):
        self._url_to_type = {}

    def type(self, iri, cls):
        self._url_to_type[iri] = cls

    def vocabulary(self, types):
        for cls in types:
            self.type(cls.id(), cls)

    def load_value(self, id, value):
        cls = self._url_to_type.get(id)
        if cls is None or value is None:
            return value
        if not cls.validate_load(value):
            raise ValueError("Cannot load as %s: %r" % (cls.id(), value))
        return cls.load(value)

    def dump_value(self, id, value):
        cls = self._url_to_type.get(id)
        if cls is None or value is None:
            return value
        if not cls.validate_dump(value):
            raise ValueError("Cannot dump as %s: %r" % (cls.id(), value))
        return cls.dump(value)

    def to_values(self, d):
        """Take JSON dict, return JSON dict with rich values.
        """
        return jsonld.compact(self.expand_to_values(d), d['@context'])

    def from_values(self, d):
        """Take rich JSON dict, return plain JSON dict without rich values.
        """
        return self.compact_from_values(jsonld.expand(d), d['@context'])

    def expand_to_values(self, d):
        """Take JSON dict, return expanded dict with rich values.
        """
        return _transform_expanded(jsonld.expand(d), self.load_value)

    def compact_from_values(self, expanded, context):
        """Take expanded JSON list, return JSON dict with plain values.
        """
        return jsonld.compact(_transform_expanded(expanded, self.dump_value),
                              context)


    # JSON module style API
    def _dump_prepare(self, obj, kw):
        # XXX override original context rules?
        has_context = '@context' in obj
        context = kw.pop('context')
        if context is not None:
            obj['@context'] = context
        result = self.from_values(obj)
        if not has_context:
            del result['@context']
        return result

    def _load_finalize(self, plain_obj, context):
        has_context = '@context' in plain_obj
        if context is not None:
            plain_obj['@context'] = context
        result = self.to_values(plain_obj)
        if not has_context:
            del result['@context']
        return result

    def dump(self, obj, *args, **kw):
        plain_obj = self._dump_prepare(obj, kw)
        return json.dump(plain_obj, *args, **kw)

    def dumps(self, obj, *args, **kw):
        plain_obj = self._dump_prepare(obj, kw)
        return json.dumps(plain_obj, *args, **kw)

    def load(self, *args, **kw):
        context = kw.pop('context')
        plain_obj = json.load(*args, **kw)
        return self._load_finalize(plain_obj, context)

    def loads(self, *args, **kw):
        context = kw.pop('context')
        plain_obj = json.loads(*args, **kw)
        return self._load_finalize(plain_obj, context)

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
        result.append(_transform_value(d, transform))
    return result


def _transform_value(d, transform):
    type = d.get('@type')
    if type is None:
        return d
    value = d.get('@value')
    if value is None:
        return d
    d = d.copy()
    d['@value'] = transform(type, value)
    return d


def types(d):
    """Convenience way to specify context using type designators.
    """
    context = {}
    for term, cls in d.items():
        if isinstance(cls, type):
            type_id = cls.id()
        elif isinstance(cls, basestring):
            type_id = cls
        else:
            assert False
        # XXX can we use some better IRI for this?
        id = 'http://jsonvalue.org/internal/%s' % term
        context[term] = {
            '@id': id,
            '@type': type_id,
        }
    return context
