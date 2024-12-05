
from ast import literal_eval
import enum
from typing import Callable, Dict, List
from polyparser.io.reader import FileReader
from polyparser.lexer     import Lexer
from polyparser.lexer.rules.ignore import IgnoreLexerRule
from polyparser.lexer.rules.indentation import IndentationLexingRule
from polyparser.lexer.rules.keyword import KeywordLexerRule
from polyparser.lexer.rules.name import NameLexerRule
from polyparser.lexer.rules.string import StringLexerRule
from polyparser.lexer.token import Token
from polyparser.lexer.token.factory import TokenTypeFactory
from polyparser.parser    import FixedContextParser, Parser
from polyparser.parser.context import ParserContext
from polyparser.parser.node import BoundNode, ParserNode
from polyparser.parser.primitives.augmented import AugmentedPrimitive, AugmentedType
from polyparser.parser.primitives.branch import OrPrimitive
from polyparser.parser.primitives.call import CallPrimitive
from polyparser.parser.primitives.function import FunctionNode
from polyparser.parser.primitives.list import ListPrimitive
from polyparser.parser.primitives.token import TokenPrimitive
from polyparser.parser.stream import ParserStream

class Language:
    __lexer  : Lexer
    __parser : Parser

    def __init__(self):
        self.__lexer  = self.get_lexer  ()
        self.__parser = self.get_parser ()

    def get_lexer (self) -> Lexer:
        raise NotImplementedError()
    def get_parser (self) -> Parser:
        raise NotImplementedError()

    def parse (self, reader: "FileReader"):
        tokens = self.__lexer.try_lexing(reader)

        return self.__parser.try_parsing(tokens)
    
class PolyLanguage(Language):
    alphabet: None | enum.Enum

    augments: Dict[str, Callable]
    def __init__(self, augments: Dict[str, Callable] = {}):
        self.alphabet = None
        
        self.augments = augments

        super().__init__()
        
    def get_alphabet (self):
        if self.alphabet is None:
            type_factory = TokenTypeFactory( "pll-type-factory" )
            type_factory.add_token_type( "NAME" ) # Name
            type_factory.add_token_type( "INDENT" )  # End of Line
            type_factory.add_token_type( "STRING" )
            type_factory.add_token_type( "DASH" )
            type_factory.add_token_type( "DEFINE" )
            type_factory.add_token_type( "TWODOTS" )
            type_factory.add_token_type( "L_SQ_B" )
            type_factory.add_token_type( "R_SQ_B" )
            type_factory.add_token_type( "L_B" )
            type_factory.add_token_type( "R_B" )
            type_factory.add_token_type( "EQUALS" )
            type_factory.add_token_type( "COMMA" )
            type_factory.add_token_type( "QMARK" )
            type_factory.add_token_type( "HAT" )
            type_factory.add_token_type( "STAR" )
            type_factory.add_token_type( "PIPE" )
            type_factory.add_token_type( "PLUS" )

            self.alphabet = type_factory.as_enumeration()
        return self.alphabet
    def get_lexer(self) -> Lexer:
        alphabet = self.get_alphabet()
        
        lexer = Lexer([
            KeywordLexerRule({
                "def": alphabet.DEFINE,
                
                "=": alphabet.EQUALS,
                "/": alphabet.DASH,
                ":": alphabet.TWODOTS,
                "[": alphabet.L_SQ_B,
                "]": alphabet.R_SQ_B,
                "(": alphabet.L_B,
                ")": alphabet.R_B,
                ",": alphabet.COMMA,
                "?": alphabet.QMARK,
                
                "|": alphabet.PIPE,
                "*": alphabet.STAR,
                "^": alphabet.HAT,
                "+": alphabet.PLUS
            }),
            NameLexerRule(alphabet.NAME),
            StringLexerRule("\"", alphabet.STRING),
            IndentationLexingRule(alphabet.INDENT),
            IgnoreLexerRule(" \r")
        ])

        return lexer

    def token_parser (self) -> ParserNode:
        def as_token_primitive (*args: List[Token]):
            assert 1 <= len(args) <= 4

            stored  = ((len(args) - 1) & 1) == 1
            expects = ((len(args) - 1) & 2) == 2

            name = args[1 if stored else 0].value

            return TokenPrimitive( name, stored, literal_eval( args[-1].value ) if expects else None )

        return AugmentedPrimitive(
            ListPrimitive(
                TokenPrimitive( "DASH" ),
                AugmentedPrimitive(
                    TokenPrimitive( "DASH", stored = True ),
                    AugmentedType.OPTIONAL
                ),
                TokenPrimitive( "NAME", stored = True ),
                AugmentedPrimitive(
                    ListPrimitive(
                        TokenPrimitive("TWODOTS", stored = True),
                        TokenPrimitive("STRING", stored = True)
                    ),
                    AugmentedType.OPTIONAL
                ),
                TokenPrimitive( "DASH" )
            ),
            prim_type = as_token_primitive
        )
    def call_parser (self) -> ParserNode:
        def as_call_primitive (name: Token, *args: List[ParserNode]):
            return CallPrimitive(
                name.value,
                *args
            )

        return AugmentedPrimitive(
            ListPrimitive(
                TokenPrimitive( "NAME", stored = True ),
                AugmentedPrimitive(
                    ListPrimitive(
                        TokenPrimitive("L_B"),
                        self.list_primitive_parser(False),
                        AugmentedPrimitive(
                            ListPrimitive(
                                TokenPrimitive("COMMA"),
                                self.list_primitive_parser(False)
                            ),
                            AugmentedType.ANY_AMOUNT
                        ),
                        TokenPrimitive("R_B")
                    ),
                    AugmentedType.ANY_AMOUNT
                )
            ),
            prim_type = as_call_primitive
        )
    def list_primitive_parser (self, brackets: bool = True):
        def as_list_primitive (*primitives):
            return ListPrimitive( *primitives )
        
        primitives = [
            TokenPrimitive("L_SQ_B"),
            AugmentedPrimitive(
                CallPrimitive("primitive"),
                AugmentedType.ANY_AMOUNT
            ),
            TokenPrimitive("R_SQ_B")
        ]
        if not brackets:
            primitives = primitives[1:-1]
        return AugmentedPrimitive(
            ListPrimitive(
                *primitives
            ),
            prim_type=as_list_primitive
        )
    def simple_primitive_parser (self) -> ParserNode:
        return OrPrimitive(
            CallPrimitive( "token_primitive" ),
            CallPrimitive( "call_primitive" ),
            CallPrimitive( "list_primitive" )
        )
    def augmented_primitive_parser (self) -> ParserNode:
        def as_augmented_primitive (*args: List[Token | ParserNode]):
            assert 1 <= len(args) <= 4
            if len(args) == 1:
                return args[0]
            position = 0
            
            augment_type = None
            if ((len(args) - 1) & 1) == 1:
                type = args[0].name
                position = 1
                if type == "QMARK": 
                    augment_type = AugmentedType.OPTIONAL
                if type == "STAR" : 
                    augment_type = AugmentedType.ANY_AMOUNT
                if type == "PLUS" : 
                    augment_type = AugmentedType.AT_LEAST_ONE
            prim_type = None
            if ((len(args) - 1) & 2) == 2:
                prim_type = self.augments[args[-1].value]
            return AugmentedPrimitive( args[position], augment_type, prim_type )

        return AugmentedPrimitive(
            ListPrimitive(
                AugmentedPrimitive(
                    OrPrimitive(
                        TokenPrimitive("QMARK", True),
                        TokenPrimitive("STAR",  True),
                        TokenPrimitive("PLUS",  True)
                    ),
                    AugmentedType.OPTIONAL
                ),
                CallPrimitive("simple_primitive"),
                AugmentedPrimitive(
                    ListPrimitive(
                        TokenPrimitive("HAT", True),
                        TokenPrimitive("NAME", True)
                    ),
                    AugmentedType.OPTIONAL
                )
            ),
            prim_type=as_augmented_primitive
        )
    def or_primitive_parser (self) -> ParserNode:
        def as_or_primitive (*primitives):
            if len(primitives) == 1:
                return primitives[0]
            return OrPrimitive(*primitives)
        
        return AugmentedPrimitive(
            ListPrimitive(
                CallPrimitive( "augmented_primitive" ),
                AugmentedPrimitive(
                    ListPrimitive(
                        TokenPrimitive("PIPE"),
                        CallPrimitive( "augmented_primitive" )
                    ),
                    AugmentedType.ANY_AMOUNT
                ),
            ),
            prim_type=as_or_primitive
        )
    def primitive_parser (self) -> ParserNode:
        return CallPrimitive( "or_primitive" )

    def block_parser (self, can_be_empty = False) -> FunctionNode:
        def as_block (*prim):
            return ListPrimitive(*prim)

        target = AugmentedType.AT_LEAST_ONE
        if can_be_empty:
            target = AugmentedType.ANY_AMOUNT

        return FunctionNode(
            "block",
            AugmentedPrimitive(
                AugmentedPrimitive(
                    OrPrimitive(
                        ListPrimitive(
                            CallPrimitive( "indent" ),
                            AugmentedPrimitive( CallPrimitive("primitive"), AugmentedType.AT_LEAST_ONE )
                        ),
                        CallPrimitive( "function", CallPrimitive("indent") )
                    ),
                    target
                ),
                prim_type=as_block
            ),
            [ "indent" ]
        )
    def function_parser (self):
        def as_function (name: Token, *args: List[Token | ParserNode]):
            name = name.value
            target = args[-1]

            args = args[:-1]

            has_target_type = False
            argnames = []
            for token in args:
                if token.name == "TWODOTS":
                    has_target_type = True
                    break
                argnames.append( token.value )
            
            if has_target_type:
                target = AugmentedPrimitive(
                    target,
                    prim_type=self.augments[args[-1].value]
                )
            
            return FunctionNode( name, target, argnames )
        return FunctionNode(
            "function",
            AugmentedPrimitive(
                ListPrimitive(
                    CallPrimitive("indent"),
                    TokenPrimitive( "DEFINE", False ),
                    TokenPrimitive( "NAME",   True ),
                    AugmentedPrimitive(
                        ListPrimitive(
                            TokenPrimitive("L_B"),
                            TokenPrimitive("NAME", True),
                            AugmentedPrimitive(
                                ListPrimitive(
                                    TokenPrimitive("COMMA"),
                                    TokenPrimitive("NAME", True)
                                ),
                                AugmentedType.ANY_AMOUNT
                            ),
                            TokenPrimitive("R_B")
                        ),
                        AugmentedType.ANY_AMOUNT
                    ),
                    AugmentedPrimitive(
                        ListPrimitive(
                            TokenPrimitive("TWODOTS", True),
                            TokenPrimitive("NAME", True)
                        ),
                        AugmentedType.OPTIONAL
                    ),
                    TokenPrimitive( "EQUALS", False ),
                    CallPrimitive( "block", ListPrimitive( CallPrimitive("indent"), TokenPrimitive("INDENT") ) )
                ),
                prim_type=as_function
            ),
            [ "indent" ]
        )

    def get_parser(self) -> Parser:
        context = ParserContext()
        stream  = ParserStream ([])

        FunctionNode( "token_primitive",  self.token_parser(), [] ).evaluate( stream, context )
        FunctionNode( "call_primitive",   self.call_parser (), [] ).evaluate( stream, context )
        FunctionNode( "list_primitive",   self.list_primitive_parser(), [] ).evaluate( stream, context )

        FunctionNode( "simple_primitive", self.simple_primitive_parser(), [] ).evaluate( stream, context )
        FunctionNode( "augmented_primitive", self.augmented_primitive_parser(), [] ).evaluate( stream, context )
        FunctionNode( "or_primitive", self.or_primitive_parser(), [] ).evaluate( stream, context )
        FunctionNode( "primitive", self.primitive_parser(), [] ).evaluate( stream, context )

        self.block_parser().evaluate( stream, context )
        self.function_parser().evaluate( stream, context )

        FunctionNode( "main", CallPrimitive( "block", ListPrimitive() ), [] ).evaluate( stream, context )

        return FixedContextParser(context)

class SourceLanguage (Language):
    def __init__(self):
        super().__init__()
    def get_entry_point (self) -> str:
        return "main"
    def get_transcripts (self) -> Dict[str, Callable]:
        raise NotImplementedError()
    def get_poly_language_source (self) -> FileReader:
        raise NotImplementedError()
    def get_parser(self) -> Parser:
        source   = self.get_poly_language_source()
        augments = self.get_transcripts()

        poly_language = PolyLanguage( augments )
        result = poly_language.parse( source )
        if len(result) == 1 and isinstance(result[0], ListPrimitive):
            result = result[0].get_primitives()

        context = ParserContext()
        stream  = ParserStream ([])

        for primitive in result:
            assert isinstance(primitive, FunctionNode), "Top level primitives can only be functions"

            primitive.evaluate( stream, context )
        return FixedContextParser( context, self.get_entry_point() )
