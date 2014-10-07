JsonValue
=========

Introduction
------------

JsonValue is a Python library that allows you to use rich Python
values with JSON. JsonValue lets you process JSON and convert it into
Python objects. You can also take Python objects and convert them into
JSON.

JsonValue is much more than the simple JSON encoder you may know from
Django or other places. JsonValue lets you also reliably decode such
serialized values. Moreover, JsonValue lets you work with complex
nested objects too and convert them to and from JSON.

JsonValue is fully pluggable with custom data types.

JsonValue is standards-based. It is based on the W3C recommendation
`JSON-LD`_. JSON-LD lets you describe the types of nodes and values in
your JSON structure in a flexible, standard way. JsonValue builds on
the JSON-LD processing library pyld_. You don't need to understand the
details of JSON-LD to make good use of JsonValue.

.. _`JSON-LD`: http://json-ld.org/

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

