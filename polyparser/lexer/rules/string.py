
from polyparser.io.reader import FileReader
from polyparser.lexer.rules.abstract import LexerRule
from polyparser.lexer.token import Token
from polyparser.lexer.token.type import TokenType
from polyparser.utils.optional import Optional

"""
This class represents a lexing rule that lexes strings

Further information is available at : https://polympiads.github.io/polyparser/reference/api/lexer.html#module-string-class-stringlexerrule
"""
class StringLexerRule(LexerRule):
    def __init__(self, sequence: str, token_type: TokenType):
        self.sequence   = sequence
        self.token_type = token_type
    
    def poll_sequence (self, reader: "FileReader"):
        with reader as (atomic, state):
            if len(state) < len(self.sequence):
                return False
            
            for i in range(len( self.sequence )):
                if state.poll() != self.sequence[i]:
                    atomic.rollback()
                    return False
            
            return True

    def try_lexing(self, reader: FileReader) -> Optional[Token]:
        with reader as (atomic, state):
            if not self.poll_sequence(reader):
                atomic.rollback()
                return None

            while len(state) != 0:
                if self.poll_sequence(reader):
                    return Optional(Token(self.token_type, state.as_position()))
                if state.poll() == '\\':
                    state.poll()

            atomic.rollback()
