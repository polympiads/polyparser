
import string

import pytest
from polyparser.io.reader import FileReader
from polyparser.lexer import Lexer
from polyparser.lexer.rules.ignore import IgnoreLexerRule
from polyparser.lexer.rules.keyword import KeywordLexerRule
from polyparser.lexer.rules.name import NameLexerRule
from polyparser.lexer.rules.string import StringLexerRule


def test_lexer_eq_neq_set ():
    lexer = Lexer( [ KeywordLexerRule({ "==": "EQ", "=": "SET", "!=": "NEQ" }) ] )

    reader = FileReader( "tests/lexer/rules/file_tests/eq-neq-set.txt" )

    tokens = lexer.try_lexing( reader )

    assert len(tokens) == 4

    with reader as (atomic, state): 
        assert len(state) == 0

    eq1 = tokens[0]
    assert   eq1.token_type == "EQ" \
         and eq1.position.line == 1 \
         and eq1.position.column == 1 \
         and eq1.position.last_column == 3 \
         and eq1.position.height == 1
    eq2 = tokens[1]
    assert   eq2.token_type == "SET" \
         and eq2.position.line == 1 \
         and eq2.position.column == 3 \
         and eq2.position.last_column == 4 \
         and eq2.position.height == 1
    eq3 = tokens[2]
    assert   eq3.token_type == "NEQ" \
         and eq3.position.line == 1 \
         and eq3.position.column == 4 \
         and eq3.position.last_column == 6 \
         and eq3.position.height == 1
    eq4 = tokens[3]
    assert   eq4.token_type == "SET" \
         and eq4.position.line == 1 \
         and eq4.position.column == 6 \
         and eq4.position.last_column == 7 \
         and eq4.position.height == 1

def test_lexer_fail ():
    reader = FileReader( "tests/lexer/rules/file_tests/simple-name.txt" )
    
    lexer = Lexer( [ NameLexerRule("NAME"), IgnoreLexerRule(string.whitespace + ".,;") ] )

    with pytest.raises(AssertionError):
        tokens = lexer.try_lexing(reader)

def test_json_lexer ():
    reader = FileReader( "tests/lexer/rules/file_tests/json-file-test.json" )
    lexer  = Lexer( [
        KeywordLexerRule(
            {
                "{": "LCB", "}": "RCB",
                "[": "LSB", "]": "RSB",
                ":": "BIND", ",": "COMMA"
            }
        ),
        StringLexerRule( "\"", "STRING" ),
        IgnoreLexerRule(string.whitespace)
    ] )

    lines = reader.content.split("\n")
    token_per_line = [[] for _ in range(len(lines))]

    for token in lexer.try_lexing(reader):
        token_per_line[token.position.line - 1].append( token )
    
    for line, tokens in zip(lines, token_per_line):
        appears = [False for _ in range(len(line))]
        for token in tokens:
            for index in range(token.position.column - 1, token.position.last_column - 1):
                appears[index] = True
        
        for index in range(len(line)):
            assert appears[index] != line[index].isspace()
