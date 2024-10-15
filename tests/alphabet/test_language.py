
import pytest
from polyparser.languages.language import Language


def test_exceptions ():
    with pytest.raises(NotImplementedError):
        language = Language()
    with pytest.raises(NotImplementedError):
        Language.get_lexer(object())
    with pytest.raises(NotImplementedError):
        Language.get_parser(object())
