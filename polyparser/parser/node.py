
from typing import Any, List, Tuple
from polyparser.parser.context import ParserContext
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream

import enum

class ParserNodeType(enum.Enum):
    PRIMITIVE = 0
    FUNCTION  = 1

class ParserNode:
    def call (self, stream: ParserStream, context: ParserContext, arguments: List[Any]):
        raise NotImplementedError()
    def evaluate (self, stream: ParserStream, context: "ParserContext") -> ParsingResult:
        raise NotImplementedError()

class BoundNode(ParserNode):
    __sub_node: ParserNode
    __context : ParserContext

    def __init__(self, node: ParserNode, context: ParserContext) -> None:
        super().__init__()

        self.__sub_node = node
        self.__context  = context
    
    def call(self, stream: ParserStream, context: ParserContext, arguments: List[Any]):
        return self.__sub_node.call(stream, self.__context, arguments)
    def evaluate(self, stream: ParserStream, context: ParserContext) -> ParsingResult:
        return self.__sub_node.evaluate(stream, self.__context)
