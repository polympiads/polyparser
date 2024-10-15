
import enum
from typing import Any
from polyparser.parser.context import ParserContext
from polyparser.parser.node import ParserNode
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream

class AugmentedType(enum.Enum):
    NONE         = 0
    OPTIONAL     = 1
    AT_LEAST_ONE = 2
    ANY_AMOUNT   = 3

class AugmentedPrimitive (ParserNode):
    def __init__(self, subprimitive: ParserNode, augment: AugmentedType = AugmentedType.NONE, prim_type: Any = None) -> None:
        self.__sub_primitive = subprimitive
        self.__augment       = augment
        self.__prim_type     = prim_type
    
    def evaluate(self, stream: ParserStream, context: ParserContext) -> ParsingResult:
        min_amount = 0
        if (self.__augment.value & 1) == 0:
            min_amount = 1
        max_amount = -1
        if (self.__augment.value & 2) == 0:
            max_amount = 1

        with stream as (atomic, state):
            amount   = 0
            last_res = None

            while amount != max_amount:
                with stream as (subatomic, substate):
                    last_res = self.__sub_primitive.evaluate(stream, context)
                    if not last_res.is_success ():
                        break

                    if self.__prim_type is not None:
                        args = substate.poll_stored()
                        
                        try:
                            substate.store( self.__prim_type(*args) )
                        except Exception as exception:
                            print(exception)
                            subatomic.rollback()
                            last_res = ParsingResult.FAILED
                            break
                    
                    amount += 1

            if amount == 0:
                if min_amount == 0:
                    return ParsingResult.IGNORED
                return last_res
            return ParsingResult.SUCCESS
