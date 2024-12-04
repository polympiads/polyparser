
from typing import List
from polyparser.io.reader import FileReader
from polyparser.lexer.rules.abstract import LexerRule
from polyparser.lexer.token import Token
from polyparser.lexer.token.type import TokenType
from polyparser.utils.optional import Optional


class IndentationLexingRule (LexerRule):
    def __init__(self, token_type: TokenType) -> None:
        self.token_type = token_type
    def try_lexing(self, reader: FileReader) -> Optional[List[Token]]:
        with reader as (atomic, state):
            if state.peek() != '\n': return None
            state.poll()
            if len(state) == 0: return Optional()

            res = []
            while len(state) != 0 and state.peek() in [ ' ', '\t' ]:
                with reader as (atomic2, state2):
                    fchar = state2.poll()
                    
                    if fchar == ' ':
                        for _ in range(3):
                            if len(state2) == 0 or state2.peek() == '\n':
                                return Optional()
                            if state2.poll() != ' ':
                                assert False, "Inconsistent use of tabs in the beginning of the line"
                    
                    res.append( Token( self.token_type, state2.as_position() ) )
            
            if len(state) != 0 and state.peek() == '\n':
                return Optional()
            if len(res) == 0:
                return Optional()
            return Optional( res )
