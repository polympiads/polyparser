
import enum
import string
from polyparser.languages.language import Language
from polyparser.lexer import Lexer
from polyparser.lexer.rules.ignore import IgnoreLexerRule
from polyparser.lexer.rules.keyword import KeywordLexerRule
from polyparser.lexer.rules.string import StringLexerRule
from polyparser.lexer.token.factory import TokenTypeFactory
from polyparser.parser import FixedContextParser, Parser
from polyparser.parser.context import ParserContext
from polyparser.parser.primitives.augmented import AugmentedPrimitive, AugmentedType
from polyparser.parser.primitives.branch import OrPrimitive
from polyparser.parser.primitives.call import CallPrimitive
from polyparser.parser.primitives.list import ListPrimitive
from polyparser.parser.primitives.token import TokenPrimitive
from ast import literal_eval


class JsonLanguage(Language):
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

            # TODO the language is incomplete, add number, true, false and null

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
    def get_parser(self) -> Parser:
        alphabet = self.get_alphabet()

        context = ParserContext()

        context.set_element( "string", AugmentedPrimitive(
            TokenPrimitive("STRING", True),
            prim_type=lambda x: literal_eval(x.value)))
        context.set_element( "list", AugmentedPrimitive(
                ListPrimitive(
                    TokenPrimitive( "LSB" ),
                    AugmentedPrimitive(
                        ListPrimitive(
                            CallPrimitive( "main" ),
                            AugmentedPrimitive(
                                ListPrimitive(
                                    TokenPrimitive("COMMA"),
                                    CallPrimitive("main")),
                                augment=AugmentedType.ANY_AMOUNT),
                            AugmentedPrimitive(
                                TokenPrimitive("COMMA"),
                                augment=AugmentedType.OPTIONAL)), 
                        augment=AugmentedType.OPTIONAL),
                    TokenPrimitive( "RSB" )
                ),
                prim_type=lambda *args: list(args)))
        context.set_element( "dict.equiv", ListPrimitive(
            CallPrimitive("string"),
            TokenPrimitive("EQUIV"),
            CallPrimitive("main")))
        context.set_element( "dict", AugmentedPrimitive(
                ListPrimitive(
                    TokenPrimitive( "LCB" ),
                    AugmentedPrimitive(
                        ListPrimitive(
                            CallPrimitive( "dict.equiv" ),
                            AugmentedPrimitive(
                                ListPrimitive(
                                    TokenPrimitive("COMMA"),
                                    CallPrimitive("dict.equiv")),
                                augment=AugmentedType.ANY_AMOUNT),
                            AugmentedPrimitive(
                                TokenPrimitive("COMMA"),
                                augment=AugmentedType.OPTIONAL)), 
                        augment=AugmentedType.OPTIONAL),
                    TokenPrimitive( "RCB" )
                ),
                prim_type=lambda *args: {
                    args[i]:args[i + 1]
                    for i in range(0, len(args), 2)
                }))
        context.set_element( "main", OrPrimitive(
            CallPrimitive( "list" ),
            CallPrimitive( "dict" ),
            CallPrimitive( "string" )
        ) )

        return FixedContextParser(context)