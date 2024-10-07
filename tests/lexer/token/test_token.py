
from polyparser.lexer.token import Token
from tests.utils.immutable import check_immutable

def test_simple_token ():
    token_types = [ "a", "b", "c" ]
    positions   = [ "a", "b", "c" ]

    # We are using string as mockups for types and positions because we only care about the data.
    for token_type in token_types:
        for position in positions:
            token = Token( token_type, position )

            assert token.token_type is token_type
            assert token.position   is position

            check_immutable ( token, "token_type", "ABC", AttributeError )
            check_immutable ( token, "position",   "DEF", AttributeError )

            check_immutable ( token, "abc123", "$123", AttributeError )
            check_immutable ( token, "def234", "$456", AttributeError )
