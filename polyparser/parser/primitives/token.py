
from typing import Any, List, Tuple
from polyparser.lexer.token import Token
from polyparser.parser.context import ParserContext
from polyparser.parser.node import ParserNode, ParserNodeType
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream


class TokenPrimitive(ParserNode):
    __name    : str
    __expects : str | None
    __stored  : bool

    def __init__(self, name: str, stored: bool = False, expects: str | None = None) -> None:
        super().__init__()

        self.__name    = name
        self.__expects = expects
        self.__stored  = stored

    def is_valid (self, token: Token):
        return token.name == self.__name \
          and (self.__expects is None \
            or self.__expects == token.value)
    def call(self, stream: ParserStream, context: ParserContext, arguments: List[Any]):
        if len(arguments) == 0:
            return self.evaluate(stream, context)
        raise NotImplementedError( "A token primitive cannot be called" )
    def evaluate(self, stream: ParserStream, context: ParserContext) -> ParsingResult:
        with stream as (atomic, state):
            if state.size == 0: return ParsingResult.FAILED

            token = state.poll()

            if self.is_valid (token):
                if self.__stored:
                    state.store( token )
                return ParsingResult.SUCCESS
            else:
                atomic.rollback()
                return ParsingResult.FAILED
