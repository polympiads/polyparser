
import pytest

from polyparser.parser import Parser


def test_parser_error ():
    with pytest.raises(NotImplementedError):
        Parser()
