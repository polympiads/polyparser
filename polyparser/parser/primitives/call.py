
from typing import List
from polyparser.parser.context import ParserContext
from polyparser.parser.node import ParserNode
from polyparser.parser.primitives.list import ListPrimitive
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream


class CallPrimitive(ParserNode):
    __name: str
    __args: List[ParserNode]
    
    def __init__(self, name: str, *arguments: ParserNode) -> None:
        self.__name = name

        self.__args = list(arguments)

    def evaluate(self, stream: ParserStream, context: ParserContext) -> ParsingResult:
        target, exists = context.get_element(self.__name)

        if exists and isinstance(target, ParserNode):
            # TODO instantiate with self context
            return target.evaluate(stream, context)
        return ParsingResult.FAILED
