
from typing import Any, List, Tuple
from polyparser.parser.context import ParserContext
from polyparser.parser.node import ParserNode, ParserNodeType
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream


class ListPrimitive(ParserNode):
    __primitives: List[ParserNode]

    def __init__(self, *primitives: List[ParserNode]) -> None:
        super().__init__()

        self.__primitives = primitives
    def call(self, stream: ParserStream, context: ParserContext, arguments: List[Any]):
        if len(arguments) == 0:
            return self.evaluate(stream, context)
        
        with stream as (atomic, state):
            result = ParsingResult.IGNORED

            for subprimitive in self.__primitives:
                next_result = subprimitive.call(stream, context, arguments)

                if next_result == ParsingResult.SUCCESS:
                    result = next_result
                elif next_result == ParsingResult.FAILED:
                    atomic.rollback()
                    return ParsingResult.FAILED

            return result
    def evaluate(self, stream: ParserStream, context: ParserContext) -> ParsingResult:
        with stream as (atomic, state):
            result = ParsingResult.IGNORED

            for subprimitive in self.__primitives:
                next_result = subprimitive.evaluate(stream, context)

                if next_result == ParsingResult.SUCCESS:
                    result = next_result
                elif next_result == ParsingResult.FAILED:
                    atomic.rollback()
                    return ParsingResult.FAILED

            return result