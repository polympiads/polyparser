
from typing import List
from polyparser.parser.context import ParserContext
from polyparser.parser.node import ParserNode
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream


class ListPrimitive(ParserNode):
    primitives: List[ParserNode]

    def __init__(self, *primitives: List[ParserNode]) -> None:
        super().__init__()

        self.primitives = primitives
    def evaluate(self, stream: ParserStream, context: ParserContext) -> ParsingResult:
        with stream as (atomic, state):
            result = ParsingResult.IGNORED

            for subprimitive in self.primitives:
                next_result = subprimitive.evaluate(stream, context)

                if next_result == ParsingResult.SUCCESS:
                    result = next_result
                elif next_result == ParsingResult.FAILED:
                    atomic.rollback()
                    return ParsingResult.FAILED

            return result