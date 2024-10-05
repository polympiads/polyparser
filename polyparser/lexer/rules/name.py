
from polyparser.io.reader import FileReader
from polyparser.lexer.rules.abstract import LexerRule
from polyparser.lexer.token import Token
from polyparser.lexer.token.type import TokenType
from polyparser.utils.optional import Optional


"""
This class represents a lexing rule that lexes names

Further information is available at : https://polympiads.github.io/polyparser/reference/api/lexer.html#module-name-class-namelexerrule
"""
class NameLexerRule(LexerRule):
    def __init__(self, token_type: TokenType) -> None:
        super().__init__()

        self.token_type = token_type
    def is_valid_first (self, char: str):
        return ord('a') <= ord(char) <= ord('z') \
            or ord('A') <= ord(char) <= ord('Z') \
            or char == '_'
    def is_valid (self, char: str):
        return self.is_valid_first(char) or ord('0') <= ord(char) <= ord('9')
    def try_lexing(self, reader: FileReader) -> Optional[Token]:
        with reader as (atomic, state):
            if len(state) == 0 or not self.is_valid_first(state.peek()):
                atomic.rollback()
                return None

            state.poll()

            while len(state) != 0 and self.is_valid(state.peek()):
                state.poll()
            
            return Optional( Token(self.token_type, state.as_position()) )