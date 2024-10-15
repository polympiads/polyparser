:tocdepth: 4

.. _`utils`:

Utils
=====

This page documents the inner API of the ``polyparser.utils`` package. It possesses the following interesting modules

#. :ref:`polyparser.utils.optional <polyparser_utils_optional>` - Module containing optional objects

.. _polyparser_utils_optional:

Module ``polyparser.utils.optional``
-------------------------------------

``class Optional[T]``
~~~~~~~~~~~~~~~~~~~~~

Objects of this class represent an optional object. It possesses two immutable properties, ``exists`` and ``value``, whose values are respectively whether the optional object exists and its value if it exists.
To create it, one can do it in the following way :

#. Either create an empty object by doing ``Optional()``
#. Either create an object with a value by doing ``Optional(value)``

.. toctree::
   :hidden:

