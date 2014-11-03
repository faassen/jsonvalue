Usage
=====

.. testsetup:: *

  pass


Introduction
------------

Let's first look at what we typically do when we handle JSON in
Python.

When we have ``JSON`` text from some source, we can parse it using the
standard library ``json`` module:

.. doctest::

  >>> import json
  >>> json.loads('{"foo": "bar"}')
  {u'foo': u'bar'}

``json.loads`` creates a Python data structure that only consists of
dicts, lists, strings, numbers, booleans and ``None``.

When we want to generate JSON, we need to create a data structure with
the same restrictions, and then use ``json.dumps``:

.. doctest::

  >>> json.dumps({u'foo': u'bar'})
  '{"foo": "bar"}'

JsonValue lifts these restrictions. Instead of working with just
dicts, lists, strings, numbers, booleans and ``None`` you can work
with other values too, such as dates and datetimes. You can even
represent whole JSON nodes as a custom Python object.

An example using dates
----------------------

Let's see how this works for date objects.

First we create a JsonValue instance. This is an object that lets us
transform Python into JSON and back:

.. doctest::

  >>> import jsonvalue
  >>> jv = jsonvalue.JsonValue()

We can give ``jv`` a vocabulary of value types, so that it knows how
to handle basic value types (such as ``Integer``, ``Date``,
``DateTime``, ``Time``, ``URL`` and some others):

.. doctest::

  >>> from jsonvalue import schemaorg
  >>> jv.value_vocabulary(schemaorg.DATA_TYPE_VOCABULARY)

These particular value types are defined here:
http://schema.org/DataType.

We can now serialize an object with Python ``date`` values::

.. doctest::

  >>> from datetime import date
  >>> from jsonvalue import valuetypes
  >>> jv.dumps({u'my_date': date(2010, 1, 1)},
  ...          context=valuetypes({'my_date': schemaorg.Date}))
  '{"my_date": "2010-01-01"}'

Note that we need to specify that ``my_date`` is actually a date in
the ``types`` argument to ``dumps``. It is an error if the ``my_date``
field is not actually a Python date object (or ``None``).

We can also parse dates when we load JSON:

.. doctest::

  >>> jv.loads('{"my_date": "2010-01-01"}', context=valuetypes({'my_date': schemaorg.Date}))
  {u'my_date': datetime.date(2010, 1, 1)}

We need to give it the same ``types`` specification as we gave it for
``dumps()``. If the ``my_date`` field in the JSON cannot be parsed as
a date, this is an error.

Custom data types
-----------------

This shows how it works with dates, but how do you work with a custom
data type? Imagine we have a custom data type that represents a
user. The user is represented in JSON ala Twitter using ``@username``.

Our user object looks like this:

.. testcode::

  class User(object):
      def __init__(self, name):
          self.name = name

This is a very simple user object. In a real program we could plug in
``User`` objects that were looked up in a database. The ``User``
object could also have more fields.

We now describe how to represent this user object as JSON:

.. testcode::

  def dump_user(user, extra):
      return '@' + user.name

We also describe how we load a user object from JSON:

.. testcode::

  def load_user(o, extra):
     if not o.startswith('@'):
         raise ValueError(
             "User representation did not start with @: %s" % o)
     return User(o[1:])

Note that we refuse to load any username that does not start with a
``@`` and raise a ``ValueError`` if we see one. In a real program
``load_user`` could do other things as well, like query the database
to get a ``User`` object.

In order to plug in these functions we need to specify a custom data type:

.. doctest::

  >>> user_datatype = jsonvalue.CustomValueType(User, dump_user, load_user)

We create a ``JsonValue`` object that understands this data type:

.. doctest::

  >>> jv = jsonvalue.JsonValue()
  >>> jv.value_type(user_datatype.id(), user_datatype)

Then we can use it for dumping and loading JSON::

.. doctest::

  >>> jv.dumps({u'user': User("faassen")}, context=valuetypes({'user': user_datatype}))
  '{"user": "@faassen"}'
  >>> jv.loads('{"user": "@faassen"}', context=valuetypes({'user': user_datatype}))
  {u'user': <User object at 0x...>}

Dumping and loading objects
---------------------------

Sometimes you don't want to directly generate a JSON string but
generate a Python representation of the JSON instead. The
``dump_objects`` method transforms objects into a JSON-serializable
structure:

.. doctest::

  >>> jv.dump_objects({u'user': User("faassen")}, context=valuetypes({'user': user_datatype}))
  {u'user': '@faassen'}

You can also turn a JSON structure into objects:

.. doctest::

  >>> jv.load_objects({u'user': '@faassen'}, context=valuetypes({'user': user_datatype}))
  {u'user': <User object at 0x...>}
