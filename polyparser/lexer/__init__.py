
from typing import List
from polyparser.io.reader import FileReader
from polyparser.lexer.rules.abstract import LexerRule
from polyparser.lexer.token import Token
from polyparser.utils.optional import Optional

"""
This class represents a lexer

Further information is available at : https://polympiads.github.io/polyparser/reference/api/lexer.html#module-polyparser-lexer
"""
class Lexer:
    __rules: List[LexerRule]

    def __init__(self, rules: List[LexerRule]) -> None:
        self.__rules = list(rules)
    
    def try_lexing (self, reader: "FileReader") -> List[Token]:
        array = []

        with reader as (atomic, state):
            while len(state) != 0:
                next_token: Optional[Token] = None

                for rule in self.__rules:
                    result = rule.try_lexing(reader)
                    if result is None: continue

                    next_token = result
                    break

                if next_token is None:
                    atomic.rollback()

                    assert False
                
                if next_token.exists:
                    array.append( next_token.value )
            
            return array

