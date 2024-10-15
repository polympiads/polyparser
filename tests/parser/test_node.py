
import pytest

from polyparser.parser.context import ParserContext
from polyparser.parser.node import ParserNode
from polyparser.parser.stream import ParserStream


def test_node_interface ():
    with pytest.raises(NotImplementedError):
        context = ParserContext()
        stream  = ParserStream ([])

        node = ParserNode()
        node.evaluate( stream, context )