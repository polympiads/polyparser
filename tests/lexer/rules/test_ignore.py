from polyparser.io.reader import FileReader
from polyparser.lexer import Lexer
from polyparser.lexer.rules.ignore import IgnoreLexerRule
from polyparser.lexer.rules.name import NameLexerRule

import string

def test_ignore_rule ():
    reader = FileReader( "tests/lexer/rules/file_tests/simple-name-working.txt" )
    
    lexer = Lexer( [ NameLexerRule("NAME"), IgnoreLexerRule(string.whitespace + ".,;") ] )
    tokens = lexer.try_lexing(reader)

    content = reader.content
    remap   = lambda x: x if NameLexerRule("").is_valid(x) else ' '
    content = "".join( map(remap, content) )

    words = [ x for x in content.split(' ') if len(x) != 0 and NameLexerRule("").is_valid_first(x[0]) ]

    for (index, token) in enumerate(tokens):
        assert token.token_type == "NAME"
        assert reader.content[token.position.column - 1: token.position.last_column - 1] == words[index]