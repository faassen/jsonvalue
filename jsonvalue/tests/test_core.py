from pyld import jsonld
from jsonvalue import JsonValue, valuetypes, CustomDataType, CustomNodeType
from jsonvalue import schemaorg
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
    i=schemaorg.Time
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

    with pytest.raises(ValueError):
        jv.dump_objects(
            dict(a='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_dump_number_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.dump_objects(
            dict(b='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_dump_float_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.dump_objects(
            dict(c='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_dump_integer_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.dump_objects(
            dict(d='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    with pytest.raises(ValueError):
        jv.dump_objects(
            dict(d=1.1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_dump_text_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.dump_objects(
            dict(e=1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_dump_url_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.dump_objects(
            dict(f=1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_dump_date_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.dump_objects(
            dict(g=datetime(2010, 1, 1)),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_dump_datetime_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.dump_objects(
            dict(h=date(2010, 1, 1)),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_dump_time_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.dump_objects(
            dict(i=date(2010, 1, 1)),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_boolean_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.load_objects(
            dict(a='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_number_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.load_objects(
            dict(b='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_float_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.load_objects(
            dict(c='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_integer_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.load_objects(
            dict(d='wrong'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)

    with pytest.raises(ValueError):
        jv.load_objects(
            dict(d=1.1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_text_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.load_objects(
            dict(e=1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_url_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.load_objects(
            dict(f=1),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_date_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.load_objects(
            dict(g='2011-14-01'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_datetime_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.load_objects(
            dict(h='2011-12-01T00:64:17'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_schema_org_data_type_load_time_wrong():
    jv = JsonValue()

    jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

    with pytest.raises(ValueError):
        jv.load_objects(
            dict(i='25:10:17'),
            context=SCHEMA_ORG_DATA_TYPES_CONTEXT)


def test_node_load_dump_value():
    jv = JsonValue()

    class User(object):
        def __init__(self, name, email):
            self.name = name
            self.email = email

    def dump_user(user):
        return { 'name': user.name,
                 'email': user.email }

    def load_user(d):
        return User(d['name'], d['email'])

    user_node_type = CustomNodeType(User, dump_user, load_user)

    jv.node_type(user_node_type.id(), User, user_node_type)

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

    def dump_user(user):
        return { 'name': user.name,
                 'email': user.email }

    def load_user(d):
        return User(d['name'], d['email'])

    user_node_type = CustomNodeType(User, dump_user, load_user)

    jv.node_type(user_node_type.id(), User, user_node_type)

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
    jv = JsonValue()

    class Users(object):
        def __init__(self, users):
            self.users = users

    def dump_users(users):
        return { 'users': users.users }

    def load_users(d):
        return Users(d['users'])

    users_node_type = CustomNodeType(Users, dump_users, load_users)

    class User(object):
        def __init__(self, name, email):
            self.name = name
            self.email = email

    def dump_user(user):
        return { 'name': user.name,
                 'email': user.email }

    def load_user(d):
        return User(d['name'], d['email'])

    user_node_type = CustomNodeType(User, dump_user, load_user)

    jv.node_type(users_node_type.id(), Users, users_node_type)
    jv.node_type(user_node_type.id(), User, user_node_type)

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
