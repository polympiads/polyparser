
from typing import List

from polyparser.lexer.token import Token
from polyparser.parser.context import ParserContext
from polyparser.parser.primitives.call import CallPrimitive
from polyparser.parser.stream import ParserStream

class Parser:
    __context: ParserContext

    def __init__(self) -> None:
        self.__context = self.get_context()

    def get_context (self) -> ParserContext:
        raise NotImplementedError()
    def try_parsing (self, tokens: List[Token]):
        stream = ParserStream( tokens )

        primitive = CallPrimitive( "main" )
        context   = ParserContext( self.__context )

        with stream as (atomic, state):
            primitive.evaluate(stream, context)

            assert state.size == 0, "Could not parse everything"
            return state.poll_stored()

class FixedContextParser(Parser):
    __context: ParserContext
    def __init__(self, context: ParserContext) -> None:
        self.__context = context

        super().__init__()
    def get_context(self) -> ParserContext:
        return self.__context
