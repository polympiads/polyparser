
from polyparser.lexer.rules.keyword import KeywordLexerRule

"""
This class represents a lexing rule to ignore a set of sequences

Further information is available at : https://polympiads.github.io/polyparser/reference/api/lexer.html#module-ignore-class-ignorelexerrule
"""
class IgnoreLexerRule(KeywordLexerRule):
    def __init__(self, sequence: str | list[str]):
        sequence = list(sequence)

        super().__init__( { x: None for x in sequence } )
