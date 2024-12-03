
from typing import Any, List
from polyparser.parser.context import ParserContext
from polyparser.parser.node import BoundNode, ParserNode, ParserNodeType
from polyparser.parser.primitives.list import ListPrimitive
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream

class CallPrimitive(ParserNode):
    __name: str
    __args: List[ParserNode]
    
    def __init__(self, name: str, *arguments: ParserNode) -> None:
        self.__name = name

        self.__args = list(arguments)

    def call(self, stream: ParserStream, context: ParserContext, arguments: List[Any]):
        target, exists = context.get_element(self.__name)
        
        if exists and isinstance(target, ParserNode):
            new_args = list(map(lambda arg : BoundNode( arg, context ), self.__args))
            print(new_args, arguments)
            return target.call(stream, context, new_args + arguments)
        return ParsingResult.FAILED
    def evaluate(self, stream: ParserStream, context: ParserContext) -> ParsingResult:
        return self.call( stream, context, [] )
