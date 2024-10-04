
from polyparser.io.reader import FileReader
from polyparser.lexer.rules.keyword import KeywordLexerRule


def test_empty_rulebook ():
    rule = KeywordLexerRule({  })

    reader = FileReader( "tests/lexer/rules/file_tests/eq-neq-set.txt" )

    assert rule.try_lexing( reader ) is None

    assert reader._SaveStream__state._FileReaderState__offset == 0
def test_simple_equals_rulebook ():
    rule = KeywordLexerRule({ "==": "EQ", "=": "SET", "!=": "NEQ" })

    reader = FileReader( "tests/lexer/rules/file_tests/eq-neq-set.txt" )
    eq1 = rule.try_lexing(reader)
    assert eq1.exists \
         and eq1.value.token_type == "EQ" \
         and eq1.value.position.line == 1 \
         and eq1.value.position.column == 1 \
         and eq1.value.position.last_column == 3 \
         and eq1.value.position.height == 1
    eq2 = rule.try_lexing(reader)
    assert eq2.exists \
         and eq2.value.token_type == "SET" \
         and eq2.value.position.line == 1 \
         and eq2.value.position.column == 3 \
         and eq2.value.position.last_column == 4 \
         and eq2.value.position.height == 1
    eq3 = rule.try_lexing(reader)
    assert eq3.exists \
         and eq3.value.token_type == "NEQ" \
         and eq3.value.position.line == 1 \
         and eq3.value.position.column == 4 \
         and eq3.value.position.last_column == 6 \
         and eq3.value.position.height == 1
    eq4 = rule.try_lexing(reader)
    assert   eq4.exists \
         and eq4.value.token_type == "SET" \
         and eq4.value.position.line == 1 \
         and eq4.value.position.column == 6 \
         and eq4.value.position.last_column == 7 \
         and eq4.value.position.height == 1
    eq5 = rule.try_lexing(reader)
    assert eq5 is None