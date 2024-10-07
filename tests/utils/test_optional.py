
import pytest
from polyparser.utils.optional import Optional
from tests.utils.immutable import check_immutable


def test_has_no_object ():
    obj = Optional()

    assert not obj.exists

    with pytest.raises(AttributeError):
        obj.value
def test_has_object_none ():
    obj = Optional(None)

    assert obj.exists
    assert obj.value is None
def test_has_object ():
    obj = Optional("Hello, World !")

    assert obj.exists
    assert obj.value == "Hello, World !"
def test_immutable ():
    obj = Optional("Hello, World !")
    check_immutable( obj, "exists", "Hello !" )
    check_immutable( obj, "value", "Hello !" )
    
    check_immutable( obj, "_Optional__has_object", "Hello !" )
    check_immutable( obj, "_Optional__value", "Hello !" )
    check_immutable( obj, "abcdef123", "Hello !" )