
import pytest
from polyparser.io.reader import FileReader
from polyparser.lexer.rules.indentation import IndentationLexingRule


def test_indentation ():
    reader = FileReader.open( "tests/lexer/rules/file_tests/indentation.txt" )

    rule = IndentationLexingRule( "INDENTATION" )

    expects = [ 4, 1, 2, 0, 0, 0, 1, 0 ]
    offset  = 0

    with reader as (atomic, state):
        while len(state) != 0:
            result = rule.try_lexing(reader)

            if result is None:
                state.poll()
            else: 
                count = len(result.value) if result.exists else 0
                assert count == expects[offset]
                offset += 1
def test_wrong_indentation ():
    reader = FileReader.open( "tests/lexer/rules/file_tests/wrong-indentation.txt" )
    rule = IndentationLexingRule( "INDENTATION" )

    with pytest.raises(AssertionError, match = "Inconsistent use of tabs in the beginning of the line"):
        with reader as (atomic, state):
            while len(state) != 0:
                result = rule.try_lexing(reader)

                if result is None:
                    state.poll()
                elif result.exists:
                    assert False
