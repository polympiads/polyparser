
import enum
from typing import List
from polyparser.lexer.token.factory import TokenTypeFactory
from polyparser.lexer.token.type import TokenType


def test_empty_factory ():
    factory = TokenTypeFactory( "EmptyAlphabet" )

    EmptyAlphabet = factory.as_enumeration()

    for key in dir(EmptyAlphabet):
        assert key.startswith("__") and key.endswith("__")

    assert len(EmptyAlphabet) == 0
    assert EmptyAlphabet.__members__ == {}

def check_factory (fname: str, name_set: List[str]):
    factory = TokenTypeFactory( fname )
    for tname in name_set:
        factory.add_token_type( tname )
    
    alphabet = factory.as_enumeration()

    members = alphabet.__members__

    assert len(members)  == len(name_set)
    assert len(alphabet) == len(name_set)

    for tname in name_set:
        assert hasattr( alphabet, tname )
        
        assert members[tname].name       == tname
        assert members[tname].value.name == tname
        assert members[tname].value.factory is factory

        assert isinstance(members[tname].value, TokenType)

    for key in dir(alphabet):
        assert (key.startswith("__") and key.endswith("__")) or key in name_set

def test_single_factory ():
    check_factory("SingleAlphabet", [ "SINGLE" ])
def test_many_factory ():
    check_factory(
        "ManyAlphabet", 
        [ "A", "B", "C", "abcdef123", "defghi234" ]
    )
