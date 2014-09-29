from pyld import jsonld
from jsonvalue import JsonValue
from datetime import datetime, date


def test_expand_to_values_no_converters():
    d = {
        '@context': {
            'foo': {
                '@id': 'http://example.com/foo',
                '@type': 'http://example.com/date'
            }
        },
        'foo': '2010-01-01'
    }

    info = JsonValue()
    assert info.expand_to_values(d) == jsonld.expand(d)

def test_expand_to_values_converter():
    d = {
        '@context': {
            'foo': {
                '@id': 'http://example.com/foo',
                '@type': 'http://example.com/date'
            }
        },
        'foo': '2010-01-01'
    }

    info = JsonValue()
    def parse_date(s):
        return datetime.strptime(s, '%Y-%m-%d').date()

    info.register_converter('http://example.com/date', parse_date)

    assert info.expand_to_values(d) == [
        {
            u'http://example.com/foo':
            [{'@type': u'http://example.com/date',
              '@value': date(2010, 1, 1)}]
        }
    ]


def test_to_values():
    d = {
        '@context': {
            'foo': {
                '@id': 'http://example.com/foo',
                '@type': 'http://example.com/date'
            }
        },
        'foo': '2010-01-01'
    }

    info = JsonValue()
    def parse_date(s):
        return datetime.strptime(s, '%Y-%m-%d').date()

    info.register_converter('http://example.com/date', parse_date)

    assert info.to_values(d) == {
        '@context': {
            'foo': {
                '@id': 'http://example.com/foo',
                '@type': 'http://example.com/date'
            }
        },
        'foo': date(2010, 1, 1)
    }
