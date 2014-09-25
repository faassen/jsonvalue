JsonValue: Rich Python values for JSON
=======================================

JsonValue is a Python library that allows you to use rich Python
values in JSON objects. It lets you use native Python date for dates
for instance, but that's only scratching the surface of what's
possible.

With JsonValue you can process JSON you receive from a client and
convert it into a Python dict with Python values. You can also take a
dictionary with rich values and convert it to a dict that can be
serialized to JSON.

It is much more than the JSONEncoder you may know from Django or other
places, and not only because it features a decoder as well. JsonValue is
fully pluggable.

JsonValue is also standards based. It is based on the W3C
recommendation `JSON-LD`_. This lets you describe the types of values
in your JSON structure in a flexible, standard way. You don't need to
understand a lot of details of JSON-LD however to make good use of
JsonValue.

.. `JSON-LD`_: http://json-ld.org/
