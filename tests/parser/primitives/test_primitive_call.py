
from polyparser.parser.context import ParserContext
from polyparser.parser.primitives.call import CallPrimitive
from polyparser.parser.primitives.token import TokenPrimitive
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream
from tests.parser.primitives.test_primitive_token import MockToken


def test_error_calls ():
    context = ParserContext()

    context.set_element( "name2", "not a node" )

    parser = ParserStream ( [ "abc", "def" ] )

    assert CallPrimitive( "name1" ).evaluate( parser, context ) == ParsingResult.FAILED
    assert CallPrimitive( "name2" ).evaluate( parser, context ) == ParsingResult.FAILED
def test_simple_call ():
    context = ParserContext()

    context.set_element("if", TokenPrimitive( "if", True ))

    parser = ParserStream(
        [
            MockToken("if", "if"),
            MockToken("fi", "fi")
        ]
    )

    primitive = CallPrimitive( "if" )
    assert primitive.evaluate( parser, context ) == ParsingResult.SUCCESS
    assert primitive.evaluate( parser, context ) == ParsingResult.FAILED

    with parser as (atomic, state):
        assert state._ParserCursor__arguments == [ parser.tokens[0] ]
