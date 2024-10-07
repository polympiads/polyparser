
import pytest
from polyparser.lexer.rules.abstract import LexerRule


def test_try_lexing_not_implemented ():
    object = LexerRule()

    with pytest.raises(AssertionError):
        object.try_lexing( None )
