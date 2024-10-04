
from polyparser.io.reader import FileReader
from polyparser.lexer import Lexer
from polyparser.lexer.rules.keyword import KeywordLexerRule


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
