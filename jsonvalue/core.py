from pyld import jsonld

class JsonValue(object):
    def __init__(self):
        self._dumpers = {}
        self._loaders = {}

    def type(self, type, dump, load):
        self._dumpers[type] = dump
        self._loaders[type] = load

    def load(self, type, value):
        load = self._loaders.get(type)
        if load is None:
            return value
        return load(value)

    def dump(self, type, value):
        dump = self._dumpers.get(type)
        if dump is None:
            return value
        return dump(value)

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
        return _transform_expanded(jsonld.expand(d), self.load)

    def compact_from_values(self, expanded, context):
        """Take expanded JSON list, return JSON dict with plain values.
        """
        return jsonld.compact(_transform_expanded(expanded, self.dump),
                              context)


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
