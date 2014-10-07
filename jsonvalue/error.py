class ValueLoadError(Exception):
    def __init__(self, term, type, value):
        self.term = term
        self.type = type
        self.value = value


class LoadError(Exception):
    def __init__(self, errors):
        self.errors = errors


class ValueDumpError(Exception):
    def __init__(self, term, type, value):
        self.term = term
        self.type = type
        self.value = value


class DumpError(Exception):
    def __init__(self, errors):
        self.errors = errors
