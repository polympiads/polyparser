
from typing import Any, List
import pytest
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

        with stream as (_a, _s):
            with pytest.raises(NotImplementedError, match="A token primitive cannot be called"):
                with stream as (atomic, state):
                    result = primitive.call(stream, ctx, [ "args" ])
            _a.rollback()
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
            atomic.rollback()
        with stream as (atomic, state):
            result = primitive.call(stream, ctx, [])
            if should_work:
                assert result == ParsingResult.SUCCESS

                args = state.poll_stored()
                assert len(args) == 1 and args[0] is tokens[1]
            else:
                assert result == ParsingResult.FAILED
                
                args = state.poll_stored()
                assert len(args) == 0
            atomic.rollback()

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
    
def test_list_pass_args ():
    vargs = "some passed args"
    vcontext = ParserContext()
    vstream = ParserStream([])
    class C (ParserNode):
        def __init__(self) -> None:
            self.visit = 0
        def call(self, stream: ParserStream, context: ParserContext, arguments: List[Any]):
            self.visit += 1
            assert stream == vstream
            assert context == vcontext
            assert arguments == vargs
            return ParsingResult.SUCCESS
        def evaluate(self, stream: ParserStream, context: ParserContext) -> ParsingResult:
            raise NotImplementedError()
    
    p1, p2 = C(), C()
    prim = ListPrimitive( p1, p2 )
    assert prim.call( vstream, vcontext, vargs ) == ParsingResult.SUCCESS

    assert p1.visit == 1
    assert p2.visit == 1
def test_list_pass_args_ignored ():
    vargs = "some passed args"
    vcontext = ParserContext()
    vstream = ParserStream([])
    class C (ParserNode):
        def __init__(self) -> None:
            self.visit = 0
        def call(self, stream: ParserStream, context: ParserContext, arguments: List[Any]):
            self.visit += 1
            assert stream == vstream
            assert context == vcontext
            assert arguments == vargs
            return ParsingResult.IGNORED
        def evaluate(self, stream: ParserStream, context: ParserContext) -> ParsingResult:
            raise NotImplementedError()
    
    p1, p2 = C(), C()
    prim = ListPrimitive( p1, p2 )
    assert prim.call( vstream, vcontext, vargs ) == ParsingResult.IGNORED

    assert p1.visit == 1
    assert p2.visit == 1
def test_list_pass_args_failed ():
    vargs = "some passed args"
    vcontext = ParserContext()
    vstream = ParserStream([])
    class C (ParserNode):
        def __init__(self, res) -> None:
            self.visit = 0
            self.res = res
        def call(self, stream: ParserStream, context: ParserContext, arguments: List[Any]):
            self.visit += 1
            assert stream == vstream
            assert context == vcontext
            assert arguments == vargs
            return self.res
        def evaluate(self, stream: ParserStream, context: ParserContext) -> ParsingResult:
            raise NotImplementedError()
    
    ps = C( ParsingResult.IGNORED ), C( ParsingResult.SUCCESS ), C( ParsingResult.IGNORED ), C(ParsingResult.FAILED), C(ParsingResult.SUCCESS)
    prim = ListPrimitive( *ps )
    assert prim.call( vstream, vcontext, vargs ) == ParsingResult.FAILED

    assert list(map(lambda x: x.visit, ps)) == [ 1, 1, 1, 1, 0 ]
