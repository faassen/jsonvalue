from pyld import jsonld


class JsonValue(object):
    def __init__(self):
        self._url_to_type = {}

    def type(self, iri, cls):
        self._url_to_type[iri] = cls

    def load_value(self, iri, value):
        cls = self._url_to_type.get(iri)
        if cls is None or value is None:
            return value
        if not cls.validate_load(value):
            raise ValueError("Cannot load as %s: %r" % (cls.id(), value))
        return cls.load(value)

    def dump_value(self, iri, value):
        cls = self._url_to_type.get(iri)
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
    def dump(self, obj, *args, **kw):
        return json.dump(self.from_values(obj), *args, **kw)

    def dumps(self, obj, *args, **kw):
        return json.dumps(self.from_values(obj), *args, **kw)

    def load(self, *args, **kw):
        return self.to_values(json.loads(*args, **kw))

    def loads(self, *args, **kw):
        return self.to_values(json.load(*args, **kw))

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
