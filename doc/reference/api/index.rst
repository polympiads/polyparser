
.. _`api`:

API Reference
=============

This page documents the inner API of the ``polyparser`` project. The project is separated into the following modules 

#. :ref:`Input / Output <io>` - ```polyparser.io`` : responsible for file handling and generic stream objects.`
#. :ref:`Lexer <lexer>` - ```polyparser.lexer`` : handles tokenization of files.`
#. :ref:`Utils <utils>` - ```polyparser.utils`` : contains tools that can be used in multiple other packages.`

We will be using the following guidelines regarding the documentation :

#. Whenever a generic class is used, we will write ``class A[T]`` instead of ``class A(Generic[T])``, where ``T`` is a ``TypeVar`` as defined by Python's ``typing`` module.
#. Whenever a generic class is used with a type containing a bound on it, we will write ``class A[T extends B]``, where ``B`` must be an ancestor of ``T``. It is defined as ``class A(Generic[T])``, where ``T`` is a ``TypeVar`` with ``bound=B`` as defined by Python's ``typing`` module.

.. toctree::
   :hidden:

   io
   lexer
   utils