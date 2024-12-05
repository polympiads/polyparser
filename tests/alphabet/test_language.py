
import pytest
from polyparser.languages.language import Language, SourceLanguage


def test_exceptions ():
    with pytest.raises(NotImplementedError):
        language = Language()
    with pytest.raises(NotImplementedError):
        Language.get_lexer(object())
    with pytest.raises(NotImplementedError):
        Language.get_parser(object())
    with pytest.raises(NotImplementedError):
        SourceLanguage.get_poly_language_source(object())
    with pytest.raises(NotImplementedError):
        SourceLanguage.get_transcripts(object())
    assert SourceLanguage.get_entry_point(object()) == "main"