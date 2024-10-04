
from typing import List
from polyparser.io.reader import FileReader
from polyparser.lexer.rules.name import NameLexerRule
from polyparser.lexer.token import Token


def test_name_valid ():
    rule = NameLexerRule("NAME")

    for i in range(256):
        assert not rule.is_valid_first(chr(i)) or rule.is_valid(chr(i))
        
        assert rule.is_valid(chr(i)) == (
            ord('a') <= i <= ord('z')
            or ord('A') <= i <= ord('Z')
            or i == ord('_')
            or ord('0') <= i <= ord('9')
        )
        assert rule.is_valid_first(chr(i)) == (
            ord('a') <= i <= ord('z')
            or ord('A') <= i <= ord('Z')
            or i == ord('_')
        )

def test_name_rule ():
    reader = FileReader( "tests/lexer/rules/file_tests/simple-name.txt" )
    
    rule = NameLexerRule("NAME")

    tokens: List[Token] = []

    with reader as (atomic, state):
        while len(state) != 0:
            res = rule.try_lexing(reader)
            if res is None and len(state) != 0:
                state.poll()
            elif res is not None: tokens.append(res)
    
    content = reader.content
    remap   = lambda x: x if rule.is_valid(x) else ' '
    content = "".join( map(remap, content) )

    words = [ x for x in content.split(' ') if len(x) != 0 and rule.is_valid_first(x[0]) ]

    for (index, token) in enumerate(tokens):
        assert token.token_type == "NAME"
        assert reader.content[token.position.column - 1: token.position.last_column - 1] == words[index]