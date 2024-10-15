
from polyparser.parser.context import ParserContext
from polyparser.parser.primitives.branch import OrPrimitive
from polyparser.parser.primitives.list import ListPrimitive
from polyparser.parser.primitives.token import TokenPrimitive
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream
from tests.parser.primitives.test_primitive_list import AlwaysIgnore
from tests.parser.primitives.test_primitive_token import MockToken


def test_trivial_or ():
    primitive = OrPrimitive(
        TokenPrimitive( "NAME", True, "true" ),
        TokenPrimitive( "NAME", True, "false" )
    )

    def parse (string: str, expects: bool):
        stream  = ParserStream( [ MockToken( "NAME", string ) ] )
        context = ParserContext()

        with stream as (atomic, state):
            assert state.size == 1
            result = primitive.evaluate( stream, context )
            stored = state.poll_stored()

            if expects:
                assert state.size == 0
                assert result == ParsingResult.SUCCESS
                assert len(stored) == 1
                assert stored[0].name == "NAME" and stored[0].value == string
            else:
                assert state.size == 1
                assert result == ParsingResult.FAILED
                assert len(stored) == 0
    
    parse ("true", True)
    parse ("false", True)
    parse ("none", False)
    parse ("nothing", False)
def test_trivial_or_with_ignored ():
    primitive = OrPrimitive(
        AlwaysIgnore(),
        TokenPrimitive( "NAME", True, "true" ),
        TokenPrimitive( "NAME", True, "false" )
    )

    def parse (string: str, expects: bool):
        stream  = ParserStream( [ MockToken( "NAME", string ) ] )
        context = ParserContext()

        with stream as (atomic, state):
            assert state.size == 1
            result = primitive.evaluate( stream, context )
            stored = state.poll_stored()

            if expects:
                assert state.size == 0
                assert result == ParsingResult.SUCCESS
                assert len(stored) == 1
                assert stored[0].name == "NAME" and stored[0].value == string
            else:
                assert state.size == 1
                assert result == ParsingResult.IGNORED
                assert len(stored) == 0
    
    parse ("true", True)
    parse ("false", True)
    parse ("none", False)
    parse ("nothing", False)
