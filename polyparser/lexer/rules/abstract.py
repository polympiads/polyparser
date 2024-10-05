
from polyparser.io.reader import FileReader
from polyparser.lexer.token import Token
from polyparser.utils.optional import Optional


"""
This class represents an abstract lexing rule

Further information is available at : https://polympiads.github.io/polyparser/reference/api/lexer.html#package-polyparser-lexer-rules
"""
class LexerRule:
    """
    try_lexing should return None in case of an error, or Optional[Token] in case it parsed anything
    """
    def try_lexing (self, reader: "FileReader") -> Optional[Token]:
        assert False, "Not implemented"
