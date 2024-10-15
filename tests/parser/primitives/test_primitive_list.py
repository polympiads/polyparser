
from polyparser.parser.context import ParserContext
from polyparser.parser.node import ParserNode
from polyparser.parser.primitives.list import ListPrimitive
from polyparser.parser.primitives.token import TokenPrimitive
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream
from tests.parser.primitives.test_primitive_token import MockToken


class AlwaysIgnore (ParserNode):
    def evaluate(self, stream: ParserStream, context: ParserContext) -> ParsingResult:
        return ParsingResult.IGNORED

def test_simple_list ():
    primitive = ListPrimitive(
        TokenPrimitive( "DASH" ),
        TokenPrimitive( "NAME", True ),
        TokenPrimitive( "DASH" )
    )

    def test_tokens (*tokens: MockToken, should_work = False):
        stream = ParserStream(tokens)
        ctx = ParserContext()

        with stream as (atomic, state):
            result = primitive.evaluate(stream, ctx)
            if should_work:
                assert result == ParsingResult.SUCCESS

                args = state.poll_stored()
                assert len(args) == 1 and args[0] is tokens[1]
            else:
                assert result == ParsingResult.FAILED
                
                args = state.poll_stored()
                assert len(args) == 0

    test_tokens(
        MockToken( "DASH", "/" ),
        MockToken( "NAME", "DASH" ),
        MockToken( "DASH", "/" ),
        should_work=True
    )
    test_tokens(
        MockToken( "DASH", "/" ),
        MockToken( "NAME2", "DASH" ),
        MockToken( "DASH", "/" )
    )
def test_ignored_list ():
    primitive = ListPrimitive( AlwaysIgnore() )

    stream = ParserStream([ MockToken("A", "B") ])
    ctx = ParserContext()

    with stream as (atomic, state):
        assert primitive.evaluate(stream, ctx) == ParsingResult.IGNORED
        assert state.poll_stored() == []
        assert state.poll().name == "A"
    primitive = ListPrimitive( AlwaysIgnore(), TokenPrimitive( "A", True ) )

    stream = ParserStream([ MockToken("A", "B") ])
    ctx = ParserContext()

    with stream as (atomic, state):
        assert primitive.evaluate(stream, ctx) == ParsingResult.SUCCESS
        stored = state.poll_stored()
        assert len(stored) == 1 and stored[0].name == "A" and state.size == 0
    
