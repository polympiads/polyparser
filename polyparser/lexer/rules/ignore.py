
from polyparser.lexer.rules.keyword import KeywordLexerRule

class IgnoreLexerRule(KeywordLexerRule):
    def __init__(self, sequence: str | list[str]):
        sequence = list(sequence)

        super().__init__( { x: None for x in sequence } )
