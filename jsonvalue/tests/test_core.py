from pyld import jsonld
from jsonvalue import JsonValue, types
from jsonvalue import schemaorg
from datetime import datetime, date, time


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
    assert info.expand_to_values(d, d['@context']) == jsonld.expand(d)


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


    info.type('http://example.com/date', schemaorg.Date)

    expanded = info.expand_to_values(d, d['@context'])

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
    info.type('http://example.com/date', schemaorg.Date)

    values = info.to_values(d, d['@context'])
    assert values == {
        '@context': {
            'foo': {
                '@id': 'http://example.com/foo',
                '@type': 'http://example.com/date'
            }
        },
        'foo': date(2010, 1, 1)
    }

    assert info.from_values(values) == d


def test_schema_org_data_type_vocabulary():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    plain = jv.from_values(dict(
        a=True,
        b=1.2,
        c=1.4,
        d=2,
        e=u"Hello",
        f=u"http://www.example.com",
        g=date(2010, 10, 1),
        h=datetime(2011, 7, 21, 14, 32, 10),
        i=time(16, 20, 10),
    ), context=types(dict(
        a=schemaorg.Boolean,
        b=schemaorg.Number,
        c=schemaorg.Float,
        d=schemaorg.Integer,
        e=schemaorg.Text,
        f=schemaorg.URL,
        g=schemaorg.Date,
        h=schemaorg.DateTime,
        i=schemaorg.Time
    )))

    assert plain == dict(
        a=True,
        b=1.2,
        c=1.4,
        d=2,
        e=u"Hello",
        f=u"http://www.example.com",
        g='2010-10-01',
        h='2011-07-21T14:32:10',
        i='16:20:10',
    )
