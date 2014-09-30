from pyld import jsonld
from jsonvalue import JsonValue, datatypes, CustomDataType
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


SCHEMA_ORG_DATA_TYPES_CONTEXT = datatypes(dict(
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


def test_schema_org_data_type_dump_boolean_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(a='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_dump_number_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(b='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_dump_float_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(c='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_dump_integer_wrong():
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


def test_schema_org_data_type_dump_text_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(e=1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_dump_url_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(f=1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_dump_date_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(g=datetime(2010, 1, 1)),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_dump_datetime_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(h=date(2010, 1, 1)),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_dump_time_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.from_values(
            dict(i=date(2010, 1, 1)),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_boolean_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.to_values(
            dict(a='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_number_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.to_values(
            dict(b='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_float_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.to_values(
            dict(c='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_integer_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.to_values(
            dict(d='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    with pytest.raises(ValueError):
        jv.to_values(
            dict(d=1.1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_text_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.to_values(
            dict(e=1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_url_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.to_values(
            dict(f=1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_date_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.to_values(
            dict(g='2011-14-01'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_datetime_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.to_values(
            dict(h='2011-12-01T00:64:17'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_time_wrong():
    jv = JsonValue()

    jv.vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.to_values(
            dict(i='25:10:17'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_expand_nested():
    print jsonld.expand({
        '@context': {
            'name': {'@id': 'http://example.com/name',
                     '@type': 'http://example.com/nametype' },
            'email': 'http://example.com/email',
            'user': {'@id': 'http://example.com/user'},
        },
        'user': {'@type': 'http://example.com/usertype',
                 'name':'foo', 'email': 'foo@example.com'}
    })

# def test_sub_object_to_values():
#     jv = JsonValue()

#     class User(object):
#         def __init__(self, name, email):
#             self.name = name
#             self.email = email

#     def dump_user(user):
#         return { 'name': user.name,
#                  'email': user.email }

#     def load_user(d):
#         return User(d['name'], d['email'])

#     user_data_type = CustomDataType(User, dump_user, load_user)
#     jv.type(user_data_type.id(), user_data_type)

#     values = jv.to_values(
#         dict(user=dict(name='foo', email='foo@example.com')),
#         context=datatypes(dict(user=user_data_type)))
#     import pdb; pdb.set_trace()

# def test_sub_object():
#     jv = JsonValue()

#     class User(object):
#         def __init__(self, name, email):
#             self.name = name
#             self.email = email

#     def dump_user(user):
#         return { 'name': user.name,
#                  'email': user.email }

#     def load_user(d):
#         return User(d['name'], d['email'])

#     user_data_type = CustomDataType(User, dump_user, load_user)
#     jv.type(user_data_type.id(), user_data_type)

#     values = jv.from_values(
#         dict(user=User('foo', 'foo@example.com')),
#              context=datatypes(dict(user=user_data_type)))
#     assert values == {
#         'user': {
#             'name': 'foo',
#             'email': 'foo@example.com'
#         }
#     }
