:tocdepth: 4

.. _`language`:

Language Definition
===================

This page documents the inner API of the ``polyparser.language`` package. It possesses the following interesting modules and classes

#. :ref:`class Language <polyparser_language>` - Class representing a generic language
#. :ref:`class PolyLanguage <polyparser_poly_language>` - Class representing the poly language langue.
#. :ref:`class SourceLanguage <polyparser_source_language>` - Class representing a language with a source from poly language.

.. _polyparser_language:

``class Language``
~~~~~~~~~~~~~~~~~~

A language is defined by its two main methods, ``get_lexer`` and ``get_parser``,
generating the lexer and parser for the specific language. It also defines a ``parse``
method taking a ``FileReader`` that handles all the computations to parse for the language.

.. _polyparser_poly_language:

``class PolyLanguage``
~~~~~~~~~~~~~~~~~~~~~~

This language is already defined and allows you to define the parser for a language
in a simple programming language. The programming language has a simple syntax inspired
from the Scala syntax. The primitive types used by augmented primitives can be passed as
an argument to the constructor of the class. For a language to be valid, the only top level
primitives are functions. The language will then automatically call the ``main`` function that
should not take any arguments.

The respective primitives can be written in the following ways :

.. code-block:: polylanguage

    # Token Primitives

    /TOKEN/      # Expects token of type "TOKEN"
    //NAME/      # Expects token of type "NAME" and stores it in the state
    /NAME:"if"/  # Expects token of type "NAME" and value "if"
    //NAME:"if"/ # Expects token of type "NAME" and value "if"
                 # and stores it in the state

    # List Primitive

    []                 # Empty primitive
    [ /IF/ /LB/ /RB/ ] # Primitive matching "if ()"

    # Call Primitive

    name            # Call the "name" function
    block(/INDENT/) # Call the "block" function with a /INDENT/ 
    f(f, f(g))      # Call the function "f", with arguments
                    # f and f(g) that can then be called

    # Augmented Primitive

    ?//NAME/           # An optional name
    +//NAME/           # A name that can be parsed an infinite amount of 
                       # times, but needs to be parsed once.
    *[/COMMA/ //NAME/] # Parse as many times as you want 
                       # a comma followed by a name
    //STRING/^String   # Find a STRING token and then preprocess it
                       # to remove the espace characters using the
                       # String primitive type given to poly language.
    +//STRING/^String  # Find many strings and preprocess all of them.

    # Or Primitive

    # An or primitive can be created by multiple augmented primitives
    # separated by pipes to represent the choice.

    a | b | c # Choose the call primitive a or the call primitive b
              # or the primitive c.

    //STRING/^String | [] # Choose a string or an empty primitive,
                          # it is equivalent to an optional string.
    
    # Function

    # Function with no arguments and that parses a simple name
    def f =
        //NAME/
    
    # Function that parses a string and preprocesses it
    def string: String =
        //STRING/
     
    # Function that parses a string after an indentation
    # specified as an argument, and that preprocesses the string.
    def block (indent): String =
        indent //STRING/
    
    # Example on how to do a dependency / context injection
    def f(callback) =
        def g =
            ...
        callback(g)

One can write Poly Language easily in Poly Language in the following way :

.. code-block:: polylanguage

    def token_primitive: TokenPrimitive =
        /SLASH/ ?//SLASH/ //NAME/ ?[//TWODOTS/ //STRING/] /SLASH/

    def list_primitive: ListPrimitive =
        [/L_SQ_B/ *primitive /R_SQ_B/]

    def call_primitive: CallPrimitive =
        //NAME/ *[/L_B/ primitive *[/COMMA/ primitive] /R_B/]

    def simple_primitive =
        token_primitive | call_primitive | list_primitive
    def augmented_primitive: AugmentedPrimitive =
        ?[//QMARK/ | //PLUS/ | //STAR/] # ? | + | *
        simple_primitive                # sub primitive
        ?[//BIND/ //NAME/]              # 

    def or_primitive: OrPrimitive =
        augmented_primitive *[/OR/ augmented_primitive]
    def primitive = or_primitive

    def block(indent*): ListPrimitive =
        +[[indent +primitive] | function(indent)] 

    def function(indent*): Function =
        indent 
        /DEFINE/ //NAME/
        *[/LB/ //NAME/ *[/COMMA/ //NAME/] /RB/]
        /SET/
        block(indent /INDENTATION/)

    def main =
        block([]) 

.. _polyparser_source_language:

``class SourceLanguage``
~~~~~~~~~~~~~~~~~~~~~~~~

A source language is a language that generates its parser using Poly Language. The
language extending this abstract class should implement the ``get_poly_language_source``
and ``get_transcripts``, returning respectively the ``FileReader`` for the language and
the dictionnary for the primitive types of the augmented primitived of the language. One
can also implement ``get_entry_point`` returning the entry point of the parser, by default
``"main"``.


``class JsonLanguage``
~~~~~~~~~~~~~~~~~~~~~~

WARNING, this language isn't complete and does not contain the implementations for JSON
numbers, booleans or null values.
This is the main example of a ``SourceLanguage``, which is defined in the following way :

.. code-block:: python

    class JsonLanguage(SourceLanguage):
        alphabet: None | enum.Enum
        def __init__(self):
            self.alphabet = None
            
            super().__init__()
            
        def get_alphabet (self):
            if self.alphabet is None:
                type_factory = TokenTypeFactory( "json-type-factory" )
                type_factory.add_token_type( "LCB" ) # Left  Curly Bracket      '{'
                type_factory.add_token_type( "RCB" ) # Right Curly Bracket      '}'
                type_factory.add_token_type( "LSB" ) # Left  Squared Bracket    '['
                type_factory.add_token_type( "RSB" ) # Right Squared Bracket    '['

                type_factory.add_token_type( "COMMA" ) # COMMA                  ','
                type_factory.add_token_type( "EQUIV" ) # EQUIV                  ':'

                type_factory.add_token_type( "STRING" ) # String

                self.alphabet = type_factory.as_enumeration()
            return self.alphabet

        def get_lexer(self) -> Lexer:
            alphabet = self.get_alphabet()

            lexer = Lexer([
                StringLexerRule( "\"", alphabet.STRING ),
                StringLexerRule( "'",  alphabet.STRING ),
                KeywordLexerRule({
                    '{': alphabet.LCB,
                    '}': alphabet.RCB,
                    '[': alphabet.LSB,
                    ']': alphabet.RSB,
                    ',': alphabet.COMMA,
                    ':': alphabet.EQUIV
                }),
                IgnoreLexerRule(string.whitespace)
            ])

            return lexer
        def get_poly_language_source(self) -> FileReader:
            return FileReader("<json-lang>", JSON_POLY_LANGUAGE_SOURCE)
        def get_transcripts(self) -> Dict[str, Callable]:
            return {
                "String": lambda  arg  : literal_eval( arg.value ),
                "List"  : lambda *args : list( args ),
                "Map"   : lambda *args : { args[i] : args[i + 1] for i in range(0, len(args), 2) }
            }

The ``JSON_POLY_LANGUAGE_SOURCE`` contains the source code for the parser and contains the following data : 

.. code-block:: polylanguage

    def string: String =
        //STRING/
    def list: List =
        /LSB/ ?[primitive *[/COMMA/ primitive]] /RSB/
    def map: Map =
        /LCB/ 
        ?[string /EQUIV/ primitive *[/COMMA/ string /EQUIV/ primitive]]
        /RCB/

    def primitive =
        map | list | string

    def main =
        primitive

.. toctree::
   :hidden:

