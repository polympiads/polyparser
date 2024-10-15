
from typing import List
from polyparser.parser.context import ParserContext
from polyparser.parser.node import ParserNode
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream


class OrPrimitive (ParserNode):
    __primitives: List[ParserNode]

    def __init__(self, *primitives: ParserNode) -> None:
        super().__init__()

        self.__primitives = list(primitives)
    def evaluate(self, stream: ParserStream, context: ParserContext) -> ParsingResult:
        with stream as (atomic, state):
            had_one_ignored = False

            for subprimitive in self.__primitives:
                subresult = subprimitive.evaluate(stream, context)

                if subresult.is_success(): return ParsingResult.SUCCESS
                if subresult.is_ignored(): had_one_ignored = True

            if had_one_ignored:
                return ParsingResult.IGNORED
            return ParsingResult.FAILED
