
from typing import Any, List
from polyparser.parser.context import ParserContext
from polyparser.parser.node import BoundNode, ParserNode
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream


class FunctionNode(ParserNode):
    def __init__(self, name: str, target: ParserNode, args_names: List[str]):
        self.__name   = name
        self.__target = target

        self.__args_names = args_names
    
    def call(self, stream: ParserStream, context: ParserContext, arguments: List[Any]):
        if len(arguments) == len(self.__args_names):
            new_context = ParserContext( context )
            for arg_name, arg in zip(self.__args_names, arguments):
                new_context.set_element( arg_name, arg )
            
            return self.__target.evaluate( stream, new_context )
        else:
            raise NotImplementedError( f"Argument count for method '{self.__name}' is wrong, expected {len(self.__args_names)} got {len(arguments)}." )
    def evaluate(self, stream: ParserStream, context: ParserContext) -> ParsingResult:
        context.set_element( self.__name, BoundNode( self, context ) )
        return ParsingResult.IGNORED
