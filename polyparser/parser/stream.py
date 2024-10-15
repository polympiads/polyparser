
from typing import List, Type

from polyparser.lexer.token   import Token
from polyparser.io.savestream import SaveStream


class ParserStream(SaveStream["ParserCursor"]):
    tokens: List[Token]

    def __init__(self, tokens: List[Token]) -> None:
        super().__init__(ParserCursor, self)

        self.tokens = tokens
        
from polyparser.parser.cursor import ParserCursor