from pyld import jsonld
from jsonvalue import JsonValue
from datetime import datetime, date


def dump_date(d):
    return datetime.strftime(d, '%Y-%m-%d')


def load_date(s):
    return datetime.strptime(s, '%Y-%m-%d').date()


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


    info.type('http://example.com/date', dump_date, load_date)

    expanded = info.expand_to_values(d)

    assert expanded == [
        {
            u'http://example.com/foo':
            [{'@type': u'http://example.com/date',
              '@value': date(2010, 1, 1)}]
        }
    ]

    assert info.compact_from_values(expanded, d['@context']) == d


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

    info.type('http://example.com/date', dump_date, load_date)

    assert info.to_values(d) == {
        '@context': {
            'foo': {
                '@id': 'http://example.com/foo',
                '@type': 'http://example.com/date'
            }
        },
        'foo': date(2010, 1, 1)
    }
