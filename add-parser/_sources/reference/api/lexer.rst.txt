:tocdepth: 4

.. _`lexer`:

Lexer
=====

This page documents the inner API of the ``polyparser.lexer`` package. It possesses the following interesting modules and packages

#. :ref:`polyparser.lexer.token <polyparser_lexer_token>` - Package containing token classes
#. :ref:`polyparser.lexer.rules <polyparser_lexer_rules>` - Package containing lexing rules
#. :ref:`polyparser.lexer <polyparser_lexer_init>` - Module containing the lexer

.. _polyparser_lexer_token:

Package ``polyparser.lexer.token``
----------------------------------

Module ``factory`` - ``class TokenTypeFactory``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains a token type factory used to generate the alphabet of token types.

Constructor ``__init__(self, name: str)``
"""""""""""""""""""""""""""""""""""""""""

Creates a factory object, with a resulting alphabet that has the name ``name``.
The resulting alphabet is an enumeration.

Method ``add_token_type(self, name: str)``
""""""""""""""""""""""""""""""""""""""""""

Adds a token type with name ``name`` as the name of the symbol and put it into the alphabet.

Method ``as_enumeration(self)``
"""""""""""""""""""""""""""""""

Returns an enumeration representing the entire alphabet.

Module ``type`` - ``class TokenType``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``TokenType`` is a class instantiating objects that are fully immutable. 
The fields and the elements in the constructor are the ``factory`` that created it and its ``name``.

Default Module - ``class Token``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Token`` is a class instantiating objects that are fully immutable. 
The fields and the elements in the constructor are the ``token_type`` it is representing and
the ``position`` representing the position range of the token.

.. _polyparser_lexer_rules:

Package ``polyparser.lexer.rules``
----------------------------------

A lexing rule is an object possessing a single function ``try_lexing(reader: FileReader)`` that needs to return an ``Optional[Token]`` object or ``None``.

#. If the return value is ``None``, the state of the reader should have been rolled back and it means it was unsuccessful in reading any token.
#. If the return value is ``Optional()``, it means the lexing was successful and the state must have polled at least one character, but the characters were ignored (for example for whitespaces).
#. If it is ``Optional(token)``, it means the lexing was successful and the state must have polled at least one character, and they have generated a token ``token`` out of it.

The interface is described into the ``abstract`` module containing the ``LexerRule`` base class.

Module ``name`` - ``class NameLexerRule``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This rule describes the usual name lexing rule, and the token type of the name tokens must be passed in the constructor.
The lexing happens in the following way :

#. The first character must be either a letter of the english alphabet or an underscore.
#. The other characters can be either letters of the english alphabet, digits or underscores.

Module ``string`` - ``class StringLexerRule``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This rule describes the usual string lexing rule, where the starting and ending sequence is the first argument of the constructor,
and where the second argument is the token type of resulting tokens. The lexing happens in the following way :

#. If the first characters represent the starting sequence, it will continue lexing.
#. When reaching a ``\`` character, it skips the next character to create an escape sequence.
#. When it reaches the ending sequence, it stops lexing. 

Module ``keyword`` - ``class KeywordLexerRule``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This rule describes a set of keywords and operands, each having its own associated token type.
One can give a dictionnary to the constructor, where the key is the keyword or operand and the value
is the token type. They are represented as a `trie <https://en.wikipedia.org/wiki/Trie>`_ behind the hood.
When lexing, the lexer tries to find the longest prefix representing a keyword inside the trie.
If the token type of a keyword is None, then the rule will still poll the characters and return an ``Optional()``
object to tell the lexer to ignore the characters of the keyword.

Module ``ignore`` - ``class IgnoreLexerRule``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This rule describes a set of keywords and operands to ignore, it extends the ``KeywordLexerRule`` rule and expects
a string or a list of strings as its parameter in the constructor. Both are interpreted as a list of string (a string
being a list of characters which are strings of size 1). It gives the keyword rule a dictionnary associating every element
of the list with ``None``, ignoring all characters. For example, it can be used to ignore all white spaces
by giving ``string.whitespace`` as its input, telling the rule that every whitespace character should be viewed
as an ignored operand.

.. _polyparser_lexer_init:

Module ``polyparser.lexer``
---------------------------

This module contains the class ``Lexer``, that allows us to lex the entire content of a reader using a list of rules.
The constructor of the class expects a list of rules, and one can then use it to try and lex the entire reader, leading to an exception in case of an error.
One can use it in the following way using for example a json lexer (without numbers included in the lexer) :

.. code-block:: python
   :emphasize-lines: 3,4,12,14,18,19

    reader = FileReader("file.json")
    
    lexer = Lexer( [
        # Add the operands of the JSON format
        KeywordLexerRule(
            {
                "{": "LCB", "}": "RCB",
                "[": "LSB", "]": "RSB",
                ":": "BIND", ",": "COMMA"
            }
        ),
        # Add a string parser
        StringLexerRule( "\"", "STRING" ),
        # Ignore white spaces
        IgnoreLexerRule(string.whitespace)
    ] )

    # Lex the reader values
    tokens = lexer.try_lexing(reader)

.. toctree::
   :hidden:

