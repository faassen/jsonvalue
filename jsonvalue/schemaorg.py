import isodate
from datetime import datetime, date, time

class SchemaOrgType(object):
    @classmethod
    def id(cls):
        return 'http://schema.org/%s' % cls.__name__

    @staticmethod
    def validate_load(value):
        return True

    @staticmethod
    def validate_dump(value):
        return True

    @staticmethod
    def load(value):
        return value

    @staticmethod
    def dump(self, value):
        return value

class DataType(SchemaOrgType):
    pass

class Boolean(DataType):
    @staticmethod
    def validate_load(value):
        return isinstance(value, bool)

    validate_dump = validate_load

class Number(DataType):
    @staticmethod
    def validate_load(value):
        return isinstance(value, int) or isinstance(value, float)

    validate_dump = validate_load

class Float(Number):
    @staticmethod
    def load(self, value):
        return float(value)

class Integer(Number):
    @staticmethod
    def validate_load(value):
        return isinstance(value, int)

    validate_dump = validate_load

class Text(DataType):
    @staticmethod
    def validate_load(value):
        return isinstance(value, basestring)

    validate_dump = validate_load

class URL(Text):
    # XXX specific validation for URL? are paths allowed?
    pass

class Date(DataType):
    @staticmethod
    def load(value):
        return isodate.parse_date(value)

    @staticmethod
    def dump(value):
        return isodate.date_isoformat(value)

    @staticmethod
    def validate_load(value):
        return isinstance(value, basestring)

    @staticmethod
    def validate_dump(value):
        return isinstance(value, date)

class DateTime(DataType):
    @staticmethod
    def load(value):
        return isodate.parse_datetime(value)

    @staticmethod
    def dump(value):
        return isodate.datetime_isoformat(value)

    @staticmethod
    def validate_load(value):
        return isinstance(value, basestring)

    @staticmethod
    def validate_dump(value):
        return isinstance(value, datetime)

class Time(DataType):
    @staticmethod
    def load(value):
        return isodate.parse_time(value)

    @staticmethod
    def dump(value):
        return isodate.time_isoformat(value)

    @staticmethod
    def validate_load(value):
        return isinstance(value, basestring)

    @staticmethod
    def validate_dump(value):
        return isinstance(value, time)


DATA_TYPE_VOCABULARY = [DataType, Boolean, Number, Float, Integer, Text,
                        URL, Date, DateTime, Time]