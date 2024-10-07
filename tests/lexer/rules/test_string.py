
import pytest
from polyparser.io.reader import FileReader
from polyparser.lexer import Lexer
from polyparser.lexer.rules.ignore import IgnoreLexerRule
from polyparser.lexer.rules.string import StringLexerRule

import string

def test_strings ():
    all_strings = [
        "\"abcdef123\"",
        "\"abc\\\"hi\"",
        "\"abc\\nhi\""
    ]

    reader = FileReader( "tests/lexer/rules/file_tests/strings.txt" )

    lexer = Lexer( [
        StringLexerRule( "\"", "STRING" ),
        IgnoreLexerRule(string.whitespace)
    ] )

    words = lexer.try_lexing(reader)
    assert len(words) == len(all_strings)

    index = 1
    for word, str in zip(words, all_strings):
        assert word.token_type == "STRING"
        assert word.position.column == 1
        assert word.position.last_column == len(str) + 1
        assert word.position.height == 1
        assert word.position.line == index
        index += 1
def test_non_finished_string ():
    reader = FileReader( "tests/lexer/rules/file_tests/strings-false.txt" )

    lexer = Lexer( [
        StringLexerRule( "\"\"\"", "STRING" ),
        IgnoreLexerRule(string.whitespace)
    ] )

    with pytest.raises(AssertionError):
        lexer.try_lexing(reader)