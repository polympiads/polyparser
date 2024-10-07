
from polyparser.lexer.token.factory import TokenTypeFactory
from polyparser.lexer.token.type import TokenType
from tests.utils.immutable import check_immutable


def test_type_constructor ():
    names = [ "abcd", "jgtuhg", "ajdneui1234", "hello_world" ]
    factories = [
        TokenTypeFactory( "f1" ),
        TokenTypeFactory( "f2" )
    ]

    for factory in factories:
        for name in names:
            type = TokenType( factory, name )

            assert type.name    is name
            assert type.factory is factory

            check_immutable( type, "name", AttributeError )
            check_immutable( type, "factory", AttributeError )

            # somewhat random names
            check_immutable( type, "abc" + name, AttributeError )
            check_immutable( type, name + "def", AttributeError )
