from pyld import jsonld
from jsonvalue.core import TypeInfo
from datetime import datetime, date


def test_dict2values_no_converters():
    d = {
        '@context': {
            'foo': {
                '@id': 'http://example.com/foo',
                '@type': 'http://example.com/date'
            }
        },
        'foo': '2010-01-01'
    }

    info = TypeInfo()
    assert info.dict2values(d) == jsonld.expand(d)

def test_dict2values_converter():
    d = {
        '@context': {
            'foo': {
                '@id': 'http://example.com/foo',
                '@type': 'http://example.com/date'
            }
        },
        'foo': '2010-01-01'
    }

    info = TypeInfo()
    def parse_date(s):
        return datetime.strptime(s, '%Y-%m-%d').date()

    info.register_converter('http://example.com/date', parse_date)

    assert info.dict2values(d) == [
        {
            u'http://example.com/foo':
            [{'@type': u'http://example.com/date',
              '@value': date(2010, 1, 1)}]
        }
    ]


def test_objectify():
    d = {
        '@context': {
            'foo': {
                '@id': 'http://example.com/foo',
                '@type': 'http://example.com/date'
            }
        },
        'foo': '2010-01-01'
    }

    info = TypeInfo()
    def parse_date(s):
        return datetime.strptime(s, '%Y-%m-%d').date()

    info.register_converter('http://example.com/date', parse_date)

    assert info.objectify(d) == {
        '@context': {
            'foo': {
                '@id': 'http://example.com/foo',
                '@type': 'http://example.com/date'
            }
        },
        'foo': date(2010, 1, 1)
    }
