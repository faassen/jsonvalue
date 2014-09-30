from pyld import jsonld
from jsonvalue import JsonValue, types
from jsonvalue import schemaorg
from datetime import datetime, date, time
import pytest


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


SCHEMA_ORG_DATA_TYPES_CONTEXT = types(dict(
    a=schemaorg.Boolean,
    b=schemaorg.Number,
    c=schemaorg.Float,
    d=schemaorg.Integer,
    e=schemaorg.Text,
    f=schemaorg.URL,
    g=schemaorg.Date,
    h=schemaorg.DateTime,
    i=schemaorg.Time
))


def test_schema_org_data_type_vocabulary_from_values():
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
    ), context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

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


def test_schema_org_data_type_vocabulary_to_values():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    values = jv.to_values(dict(
        a=True,
        b=1.2,
        c=1.4,
        d=2,
        e=u"Hello",
        f=u"http://www.example.com",
        g='2010-10-01',
        h='2011-07-21T14:32:10',
        i='16:20:10',
    ), context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    assert values == dict(
        a=True,
        b=1.2,
        c=1.4,
        d=2,
        e=u"Hello",
        f=u"http://www.example.com",
        g=date(2010, 10, 1),
        h=datetime(2011, 7, 21, 14, 32, 10),
        i=time(16, 20, 10),
    )


def test_schema_org_none_from_values():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    plain = jv.from_values(dict(
        a=None,
        b=None,
        c=None,
        d=None,
        e=None,
        f=None,
        g=None,
        h=None,
        i=None,
    ), context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    # all Nones are removed by expansion
    assert plain == {}


def test_schema_org_none_to_values():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    values = jv.to_values(dict(
        a=None,
        b=None,
        c=None,
        d=None,
        e=None,
        f=None,
        g=None,
        h=None,
        i=None,
    ), context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    # all Nones are removed by expansion
    assert values == {}


def test_schema_org_data_type_boolean_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(a='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_number_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(b='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_float_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(c='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_integer_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(d='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(d=1.1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_text_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(e=1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_url_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(f=1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_date_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(g=datetime(2010, 1, 1)),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_datetime_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(h=date(2010, 1, 1)),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_time_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(i=date(2010, 1, 1)),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)
