from jsonvalue import JsonValue, valuetypes, CustomNodeType, CustomValueType
from jsonvalue import schemaorg, error
from datetime import datetime, date, time
import pytest


def test_load_objects():
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
    info.value_type('http://example.com/date', schemaorg.Date)

    values = info.load_objects(d, d['@context'])
    assert values == {
        '@context': {
            'foo': {
                '@id': 'http://example.com/foo',
                '@type': 'http://example.com/date'
            }
        },
        'foo': date(2010, 1, 1)
    }

    assert info.dump_objects(values) == d


SCHEMA_ORG_DATA_TYPES_CONTEXT = valuetypes(dict(
    a=schemaorg.Boolean,
    b=schemaorg.Number,
    c=schemaorg.Float,
    d=schemaorg.Integer,
    e=schemaorg.Text,
    f=schemaorg.URL,
    g=schemaorg.Date,
    h=schemaorg.DateTime,
    i=schemaorg.Time,
    sub='http://jsonvalue.org/sub',
))


def test_schema_org_data_type_vocabulary_dump_objects_flat():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    plain = jv.dump_objects(dict(
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


def test_schema_org_data_type_vocabulary_load_objects():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    values = jv.load_objects(dict(
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


def test_schema_org_data_type_vocabulary_load_objects_nested():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    context = {
        "a": {
            '@id': 'http://example.com/a',
            '@type': schemaorg.Integer.id()
        },
        "b": {
            '@id': 'http://example.com/b',
            '@type': schemaorg.Date.id()
        },
        "sub": 'http://example.com/sub'
    }

    values = jv.load_objects({
        'a': 3,
        'sub': {
            'b': '2011-01-01'
        }
    }, context=context)

    assert values == {
        'a': 3,
        'sub': {
            'b': date(2011, 1, 1)
        }
    }

    values = jv.load_objects({
        'a': 3,
        'sub': {
            '@type': 'http://example.com/nanah/type',
            'b': '2011-01-01'
        }
    }, context=context)

    assert values == {
        'a': 3,
        'sub': {
            '@type': 'http://example.com/nanah/type',
            'b': date(2011, 1, 1)
        }
    }


def test_schema_org_data_type_vocabulary_dump_objects_nested():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    context = {
        "a": {
            '@id': 'http://example.com/a',
            '@type': schemaorg.Integer.id()
        },
        "b": {
            '@id': 'http://example.com/b',
            '@type': schemaorg.Date.id()
        },
        "sub": 'http://example.com/sub'
    }

    values = jv.dump_objects({
        'a': 3,
        'sub': {
            'b': date(2011, 1, 1)
        }
    }, context=context)

    assert values == {
        'a': 3,
        'sub': {
            'b': '2011-01-01'
        }
    }

    values = jv.dump_objects({
        'a': 3,
        'sub': {
            '@type': 'http://example.com/nanah/type',
            'b': date(2011, 1, 1)
        }
    }, context=context)

    assert values == {
        'a': 3,
        'sub': {
            '@type': 'http://example.com/nanah/type',
            'b': '2011-01-01'
        }
    }


def test_schema_org_none_dump_objects():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    plain = jv.dump_objects(dict(
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


def test_schema_org_none_load_objects():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    values = jv.load_objects(dict(
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

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.DumpError) as e:
        jv.dump_objects(
            dict(a='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)
    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/a'
    assert errors[0].type == 'http://schema.org/Boolean'
    assert errors[0].value == 'wrong'


def test_schema_org_data_type_dump_number_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.DumpError) as e:
        jv.dump_objects(
            dict(b='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)
    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/b'
    assert errors[0].type == 'http://schema.org/Number'
    assert errors[0].value == 'wrong'


def test_schema_org_data_type_dump_float_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.DumpError) as e:
        jv.dump_objects(
            dict(c='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)
    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/c'
    assert errors[0].type == 'http://schema.org/Float'
    assert errors[0].value == 'wrong'


def test_schema_org_data_type_dump_integer_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.DumpError) as e:
        jv.dump_objects(
            dict(d='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/d'
    assert errors[0].type == 'http://schema.org/Integer'
    assert errors[0].value == 'wrong'

    with pytest.raises(error.DumpError) as e:
        jv.dump_objects(
            dict(d=1.1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/d'
    assert errors[0].type == 'http://schema.org/Integer'
    assert errors[0].value == 1.1


def test_schema_org_data_type_dump_text_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.DumpError) as e:
        jv.dump_objects(
            dict(e=1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/e'
    assert errors[0].type == 'http://schema.org/Text'
    assert errors[0].value == 1


def test_schema_org_data_type_dump_url_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.DumpError) as e:
        jv.dump_objects(
            dict(f=1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/f'
    assert errors[0].type == 'http://schema.org/URL'
    assert errors[0].value == 1


def test_schema_org_data_type_dump_date_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.DumpError) as e:
        jv.dump_objects(
            dict(g=datetime(2010, 1, 1)),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/g'
    assert errors[0].type == 'http://schema.org/Date'
    assert errors[0].value == datetime(2010, 1, 1)


def test_schema_org_data_type_dump_datetime_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.DumpError) as e:
        jv.dump_objects(
            dict(h=date(2010, 1, 1)),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/h'
    assert errors[0].type == 'http://schema.org/DateTime'
    assert errors[0].value == date(2010, 1, 1)


def test_schema_org_data_type_dump_time_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.DumpError) as e:
        jv.dump_objects(
            dict(i=date(2010, 1, 1)),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/i'
    assert errors[0].type == 'http://schema.org/Time'
    assert errors[0].value == date(2010, 1, 1)


def test_schema_org_data_type_load_boolean_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.LoadError) as e:
        jv.load_objects(
            dict(a='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/a'
    assert errors[0].type == 'http://schema.org/Boolean'
    assert errors[0].value == 'wrong'


def test_schema_org_data_type_load_number_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.LoadError) as e:
        jv.load_objects(
            dict(b='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/b'
    assert errors[0].type == 'http://schema.org/Number'
    assert errors[0].value == 'wrong'


def test_schema_org_data_type_load_float_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.LoadError) as e:
        jv.load_objects(
            dict(c='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/c'
    assert errors[0].type == 'http://schema.org/Float'
    assert errors[0].value == 'wrong'


def test_schema_org_data_type_load_integer_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.LoadError) as e:
        jv.load_objects(
            dict(d='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/d'
    assert errors[0].type == 'http://schema.org/Integer'
    assert errors[0].value == 'wrong'

    with pytest.raises(error.LoadError) as e:
        jv.load_objects(
            dict(d=1.1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/d'
    assert errors[0].type == 'http://schema.org/Integer'
    assert errors[0].value == 1.1


def test_schema_org_data_type_load_text_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.LoadError) as e:
        jv.load_objects(
            dict(e=1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/e'
    assert errors[0].type == 'http://schema.org/Text'
    assert errors[0].value == 1


def test_schema_org_data_type_load_url_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.LoadError) as e:
        jv.load_objects(
            dict(f=1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/f'
    assert errors[0].type == 'http://schema.org/URL'
    assert errors[0].value == 1


def test_schema_org_data_type_load_date_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.LoadError) as e:
        jv.load_objects(
            dict(g='2011-14-01'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/g'
    assert errors[0].type == 'http://schema.org/Date'
    assert errors[0].value == '2011-14-01'


def test_schema_org_data_type_load_datetime_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.LoadError) as e:
        jv.load_objects(
            dict(h='2011-12-01T00:64:17'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/h'
    assert errors[0].type == 'http://schema.org/DateTime'
    assert errors[0].value == '2011-12-01T00:64:17'

    with pytest.raises(error.LoadError) as e:
        jv.load_objects(
            dict(h='2011-12-01'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/h'
    assert errors[0].type == 'http://schema.org/DateTime'
    assert errors[0].value == '2011-12-01'


def test_schema_org_data_type_load_time_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.LoadError) as e:
        jv.load_objects(
            dict(i='25:10:17'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://jsonvalue.org/internal/id/i'
    assert errors[0].type == 'http://schema.org/Time'
    assert errors[0].value == '25:10:17'


def test_multiple_errors_dump_value():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.DumpError) as e:
        jv.dump_objects(
            dict(a='wrong', b='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 2

    assert errors[0].term == 'http://jsonvalue.org/internal/id/a'
    assert errors[0].type == 'http://schema.org/Boolean'
    assert errors[0].value == 'wrong'

    assert errors[1].term == 'http://jsonvalue.org/internal/id/b'
    assert errors[1].type == 'http://schema.org/Number'
    assert errors[1].value == 'wrong'


def test_multiple_errors_nested_dump_value():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.DumpError) as e:
        jv.dump_objects(
            dict(a='wrong', sub=dict(b='wrong')),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 2

    assert errors[0].term == 'http://jsonvalue.org/internal/id/a'
    assert errors[0].type == 'http://schema.org/Boolean'
    assert errors[0].value == 'wrong'

    assert errors[1].term == 'http://jsonvalue.org/internal/id/b'
    assert errors[1].type == 'http://schema.org/Number'
    assert errors[1].value == 'wrong'


def test_multiple_errors_load_value():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.LoadError) as e:
        jv.load_objects(
            dict(a='wrong', b='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 2

    assert errors[0].term == 'http://jsonvalue.org/internal/id/a'
    assert errors[0].type == 'http://schema.org/Boolean'
    assert errors[0].value == 'wrong'

    assert errors[1].term == 'http://jsonvalue.org/internal/id/b'
    assert errors[1].type == 'http://schema.org/Number'
    assert errors[1].value == 'wrong'


def test_multiple_errors_nested_load_value():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(error.LoadError) as e:
        jv.load_objects(
            dict(a='wrong', sub=dict(b='wrong')),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    errors = e.value.errors
    assert len(errors) == 2

    assert errors[0].term == 'http://jsonvalue.org/internal/id/a'
    assert errors[0].type == 'http://schema.org/Boolean'
    assert errors[0].value == 'wrong'

    assert errors[1].term == 'http://jsonvalue.org/internal/id/b'
    assert errors[1].type == 'http://schema.org/Number'
    assert errors[1].value == 'wrong'


def test_node_load_dump_value():
    jv = JsonValue()

    class User(object):
        def __init__(self, name, email):
            self.name = name
            self.email = email

    def dump_user(user, extra):
        return {
            'name': user.name,
            'email': user.email
        }

    def load_user(d, extra):
        return User(d['name'], d['email'])

    context = {
        'name': {
            '@id': 'http://example.com/name',
            '@type': schemaorg.Text.id(),
        },
        'email': {
            '@id': 'http://example.com/email',
            '@type': schemaorg.Text.id(),
        },
        'user': 'http://example.com/user',
    }

    user_node_type = CustomNodeType(User, dump_user, load_user, context)

    jv.node_type(user_node_type.id(), user_node_type)

    json = {
        'user': {
            '@type': user_node_type.id(),
            'name': 'foo',
            'email': 'foo@example.com'
        }
    }
    values = jv.load_objects(json, context=context)

    assert len(values) == 1
    assert isinstance(values['user'], User)
    assert values['user'].name == 'foo'
    assert values['user'].email == 'foo@example.com'

    json_out = jv.dump_objects(values, context=context)
    assert json_out == json


def test_outer_node_to_value():
    jv = JsonValue()

    class User(object):
        def __init__(self, name, email):
            self.name = name
            self.email = email

    def dump_user(user, extra):
        return {
            'name': user.name,
            'email': user.email
        }

    def load_user(d, extra):
        return User(d['name'], d['email'])

    context = {
        'name': {
            '@id': 'http://example.com/name',
            '@type': schemaorg.Text.id(),
        },
        'email': {
            '@id': 'http://example.com/email',
            '@type': schemaorg.Text.id(),
        }
    }

    user_node_type = CustomNodeType(User, dump_user, load_user, context)

    jv.node_type(user_node_type.id(), user_node_type)

    json = {
        '@type': user_node_type.id(),
        'name': 'foo',
        'email': 'foo@example.com'
    }

    values = jv.load_objects(json, context=context)

    assert isinstance(values, User)
    assert values.name == 'foo'
    assert values.email == 'foo@example.com'

    json_out = jv.dump_objects(values, context=context)
    assert json_out == json


def test_nested_node_values():
    context = {
        'name': {
            '@id': 'http://example.com/name',
            '@type': schemaorg.Text.id(),
        },
        'email': {
            '@id': 'http://example.com/email',
            '@type': schemaorg.Text.id(),
        },
        'users': 'http://example.com/users'
    }

    jv = JsonValue()

    class Users(object):
        def __init__(self, users):
            self.users = users

    def dump_users(users, extra):
        return {
            'users': users.users
        }

    def load_users(d, extra):
        return Users(d['users'])

    users_node_type = CustomNodeType(Users, dump_users, load_users, context)

    class User(object):
        def __init__(self, name, email):
            self.name = name
            self.email = email

    def dump_user(user, extra):
        return {
            'name': user.name,
            'email': user.email
        }

    def load_user(d, extra):
        return User(d['name'], d['email'])

    user_node_type = CustomNodeType(User, dump_user, load_user, context)

    jv.node_type(users_node_type.id(), users_node_type)
    jv.node_type(user_node_type.id(), user_node_type)

    json = {
        '@type': users_node_type.id(),
        'users': [
            {
                '@type': user_node_type.id(),
                'name': 'foo',
                'email': 'foo@example.com',
            },
            {
                '@type': user_node_type.id(),
                'name': 'bar',
                'email': 'bar@example.com',
            },
        ]
    }
    values = jv.load_objects(json, context=context)

    assert isinstance(values, Users)
    assert len(values.users) == 2
    user1 = values.users[0]
    user2 = values.users[1]

    assert user1.name == 'foo'
    assert user1.email == 'foo@example.com'

    assert user2.name == 'bar'
    assert user2.email == 'bar@example.com'

    json_out = jv.dump_objects(values, context=context)
    assert json_out == json


def test_unknown_value_type():
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

    # we register no type for http://example.com/date. This value
    # is therefore passed through literally
    values = info.load_objects(d, d['@context'])
    assert values == {
        '@context': {
            'foo': {
                '@id': 'http://example.com/foo',
                '@type': 'http://example.com/date'
            }
        },
        'foo': '2010-01-01'
    }

    assert info.dump_objects(values) == d

    # we can however instruct the system to bail out as soon as
    # a unrecognized value type is recognized
    with pytest.raises(error.LoadError) as e:
        info.load_objects(d, d['@context'], reject_unknown=True)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://example.com/foo'
    assert errors[0].type == 'http://example.com/date'
    assert errors[0].value == '2010-01-01'


def test_missing_value_type():
    # we don't declare a value type for 'foo'
    d = {
        '@context': {
            'foo': {
                '@id': 'http://example.com/foo',
            }
        },
        'foo': '2010-01-01'
    }

    info = JsonValue()

    values = info.load_objects(d, d['@context'])
    assert values == {
        '@context': {
            'foo': {
                '@id': 'http://example.com/foo',
            }
        },
        'foo': '2010-01-01'
    }

    assert info.dump_objects(values) == d

    # we can however instruct the system to bail out as soon as
    # a missing value type is recognized
    with pytest.raises(error.LoadError) as e:
        info.load_objects(d, d['@context'], reject_unknown=True)

    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0].term == 'http://example.com/foo'
    assert errors[0].type is None
    assert errors[0].value == '2010-01-01'


def test_extra_parameters():
    d = {
        '@context': {
            'foo': {
                '@id': 'http://example.com/foo',
                '@type': 'http://example.com/x'
            },
            'bar': {
                '@id': 'http://example.com/bar',
                '@type': 'http://example.com/date',
            }
        },
        'foo': 'something',
        'bar': '2010-01-01'
    }

    info = JsonValue()

    class X(object):
        def __init__(self, value, request):
            self.value = value
            self.request = request

    def dump_x(x, request):
        return x.value + '(%s)' % request

    def load_x(o, request):
        return X(o, request)

    t = CustomValueType(X, dump_x, load_x)

    info.value_type('http://example.com/x', t)
    info.value_type('http://example.com/date', schemaorg.Date)

    request = 'my request'

    values = info.load_objects(d, d['@context'], extra=request)

    assert values['foo'].value == 'something'
    assert values['foo'].request == 'my request'
    assert values['bar'] == date(2010, 1, 1)

    json_out = info.dump_objects(values, d['@context'], extra=request)
    expected = d.copy()
    expected['foo'] = 'something(my request)'
    assert json_out == expected

