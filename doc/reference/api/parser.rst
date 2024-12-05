:tocdepth: 4

.. _`parser`:

Parser
======

This page documents the inner API of the ``polyparser.parser`` package.
The parser is structured mostly around the following objects :

#. :ref:`Context <polyparser_parser_context>` - Parsing context
#. :ref:`Cursor / Stream <polyparser_parser_cursor>` - Parser cursor and parser stream
#. :ref:`Nodes <polyparser_parser_node>` - Parser nodes (rules for parsing)

.. _polyparser_parser_context:

Module ``polyparser.parser.context``
------------------------------------

``class ParserContext``
~~~~~~~~~~~~~~~~~~~~~~~

A parser context contains the current variables,
it is similar to a classical variable container, which can be
linked to a parent variable container. It has both ``get_element``
and ``set_element`` variables to allow for getting and setting variables.

.. _polyparser_parser_cursor:

Module ``polyparser.parser.stream``
-----------------------------------

``class ParserStream(SaveStream[ParserCursor])``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This object represents a stream of tokens as well as the
values parsed with the prefix already parsed.

Module ``polyparser.parser.cursor``
-----------------------------------

``class ParserCursor(SavedState)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``ParserCursor`` is the ``SavedState`` implementation used
in the :ref:`save stream <polyparser_io_savestream>`.
It contains a list of tokens that can be polled
and peeked like a queue using the ``poll`` and ``peek`` methods.
It also contains the list of values that have been stored inside the state
as well as a way to clear this list and retrieve all of the data inside using
the ``store`` and ``poll_stored`` methods.

.. _polyparser_parser_node:

A ``ParserNode`` object represents a rule to parse the tokens inside the ``ParserStream``.
The set of primitives is described by the ``PLY-BCK 002 - PolyParser`` specification. Each
``ParserNode`` implements both the ``call`` and ``evaluate`` methods. These two methods
take a ``stream`` and ``context`` parameters for the current state of the parsing, and the
``call`` method simulates a function being called and has thus a list of ``arguments`` that
are themselves primitives or functions. They both return a parsing result, either ``FAILED``,
``SUCCESS`` or ``IGNORED``.

When the ``call`` method is called on a primitive that
does not implement a function-based architecture, if the list of arguments is empty, then it calls
the ``evaluate`` method. Otherwise, it raises an exception. This exception might not have a good
stack trace, so you need to be carefull when you write the generic parser.

Module ``polyparser.parser.primitives``
---------------------------------------

``class TokenPrimitive``
~~~~~~~~~~~~~~~~~~~~~~~~

A token primitive parses a single token with a specific name.
The constructor of the primitive takes the name of the token type
it expects, whether to store it in the state (default is ``False``) and
the expected value of the token (default is ``None`` as the value can be anything).

``class ListPrimitive``
~~~~~~~~~~~~~~~~~~~~~~~~

The list primitive has a list of sub primitives, and both methods forward
arguments to the sub primitives in order. The parser result will then be
``FAILED`` if at least one of the result is ``FAILED``, ``IGNORED`` if all of them are ``IGNORED``,
and ``SUCCESS`` if at least one of them is ``SUCCESS``. If the result is failed, the state is rolled back.

``class OrPrimitive``
~~~~~~~~~~~~~~~~~~~~~

The or primitive allows to have a branch in the parsing.
It has a list of subprimitives and tries to parse them in order,
searching for the first that is successful, and in that case 
it returns ``SUCCESS``. If none of them is successful,
and one of them is ignored, then the branch is ignored.
Otherwise, the or primitive fails.

``class AugmentedPrimitive``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The augmented primitive allows to enhance the behaviour of
a single primitive by passing its stored data in a python function
and replacing the stored data by the result of this function.
It also allows to repeat this behaviour once, making it optional, repeating
it an arbitrary amount of time, or repeating it at least one time.

``class CallPrimitive``
~~~~~~~~~~~~~~~~~~~~~~~

A call primitive allows to call a function with arguments.
If we evaluate the primitive, then it is equivalent to calling the
primitive with an empty list of arguments. If we call the primitive
with a list of arguments, then it calls the target primitive (retrieved
from the context with the given name), with the arguments from the current
call primitive bound to the current context (using a ``BoundNode``) extended by
the old arguments.

Module ``polyparser.parser.function``
-------------------------------------

``class FunctionNode``
~~~~~~~~~~~~~~~~~~~~~~

This primitive allows to represent a repetitive or recursive procedure that 
can have arguments. It is described by the name of the function, its sub procedure
and the list of argument names. When being evaluated, it would bind itself to the context
and would be stored inside the context to be called later. When being called, it would
generate a new context from the bound context and adding the arguments to the context using the argument
names in the same order.

.. toctree::
   :hidden:

