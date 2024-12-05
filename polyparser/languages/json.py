
import enum
import string
from typing import Callable, Dict
from polyparser.io.reader import FileReader
from polyparser.languages.language import SourceLanguage
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

JSON_POLY_LANGUAGE_SOURCE = """
def string: String =
    //STRING/
def list: List =
    /LSB/ ?[primitive *[/COMMA/ primitive]] /RSB/
def map: Map =
    /LCB/ ?[string /EQUIV/ primitive *[/COMMA/ string /EQUIV/ primitive]] /RCB/
def primitive =
    map | list | string
def main =
    primitive
"""

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
    def get_poly_language_source(self) -> FileReader:
        return FileReader("<json-lang>", JSON_POLY_LANGUAGE_SOURCE)
    def get_transcripts(self) -> Dict[str, Callable]:
        return {
            "String": lambda  arg  : literal_eval( arg.value ),
            "List"  : lambda *args : list( args ),
            "Map"   : lambda *args : { args[i] : args[i + 1] for i in range(0, len(args), 2) }
        }