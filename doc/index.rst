JsonValue
=========

Introduction
------------

JsonValue is a Python library that allows you to use rich Python
values in Json objects. With JsonValue you can process JSON you
receive from a client and convert it into a Python dict with Python
values. You can also take a dictionary with rich values and convert it
to a dict that can be serialized to JSON.

JsonValue can do much more than the JSONEncoder you may know from
Django or other places, and not only because it features a decoder as
well. JsonValue is fully pluggable with custom data types.

JsonValue is also standards based. It is based on the W3C
recommendation `JSON-LD`_. JSON-LD lets you describe the types of
values in your JSON structure in a flexible, standard way. You don't
need to understand the details of JSON-LD to make good use of
JsonValue.

.. _`JSON-LD`: http://json-ld.org/

JsonValue builds on the pyld_ library for its core functionality, but you
don't need to understand pyld in order to use JsonValue.

.. _pyld: https://github.com/digitalbazaar/pyld

Contents
--------

.. toctree::
   :maxdepth: 2

   usage
   changes


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

