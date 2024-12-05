
from typing import Any, List
import pytest

from polyparser.parser.context import ParserContext
from polyparser.parser.node import BoundNode, ParserNode
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream


def test_node_interface ():
    with pytest.raises(NotImplementedError):
        context = ParserContext()
        stream  = ParserStream ([])

        node = ParserNode()
        node.evaluate( stream, context )
    with pytest.raises(NotImplementedError):
        context = ParserContext()
        stream  = ParserStream ([])

        node = ParserNode()
        node.call( stream, context, [] )

def test_bound_node ():
    vcontext = ParserContext()
    vstream  = ParserStream ([])

    vargs = "some arguments, not a list but should go through"

    class BVN (ParserNode):
        def __init__(self, v1, v2):
            self.v1, self.v2 = v1, v2
        def call(self, stream: ParserStream, context: ParserContext, arguments: List[Any]):
            assert stream  == vstream
            assert context == self.v1
            assert context != self.v2
            assert context != vcontext

            assert arguments == vargs
        def evaluate(self, stream: ParserStream, context: ParserContext) -> ParsingResult:
            assert stream  == vstream
            assert context == self.v2
            assert context != self.v1
            assert context != vcontext

    bvn = BVN( ParserContext(), ParserContext() )
    
    BoundNode( bvn, bvn.v1 ).call( vstream, vcontext, vargs )
    BoundNode( bvn, bvn.v2 ).evaluate( vstream, vcontext )