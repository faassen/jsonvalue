from pyld import jsonld

class JsonValue(object):
    def __init__(self):
        self._converters = {}

    def register_converter(self, type, converter):
        self._converters[type] = converter

    def convert(self, type, value):
        converter = self._converters.get(type)
        if converter is None:
            return value
        return converter(value)

    def to_values(self, d):
        """Take JSON dict, return JSON dict with rich values.
        """
        context = d['@context'] # XXX deal with context as URLs
        d = self.expand_to_values(d)
        return jsonld.compact(d, context)

    def expand_to_values(self, d):
        """Take JSON dict, return expanded dict with rich values.
        """
        expanded = jsonld.expand(d)
        result = []
        for d in expanded:
            result.append(self.obj_to_values(d))
        return result

    def obj_to_values(self, d):
        result = {}
        for key, l in d.items():
            if not isinstance(l, list):
                result[key] = l
                continue
            result[key] = self.list_to_values(l)
        return result

    def list_to_values(self, l):
        result = []
        for d in l:
            if not isinstance(d, dict):
                result.append(d)
            result.append(self.to_value(d))
        return result

    def to_value(self, d):
        type = d.get('@type')
        if type is None:
            return d
        value = d.get('@value')
        if value is None:
            return d
        d = d.copy()
        d['@value'] = self.convert(type, value)
        return d

    def values2dict(self, d):
        """Take a dict with rich values, return dict with JSON.
        """

