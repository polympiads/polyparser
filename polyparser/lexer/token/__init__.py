
from typing import Any
from polyparser.io.position import PositionRange
from polyparser.lexer.token.type import TokenType

"""
This class represents a lexed token

Further information is available at : https://polympiads.github.io/polyparser/reference/api/lexer.html#default-module-class-token
"""
class Token:
    token_type : TokenType
    position   : PositionRange

    __locked : bool

    def __init__(self, token_type: TokenType, position: PositionRange) -> None:
        self.token_type = token_type
        self.position   = position

        self.__locked = True
    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, "_Token__locked"):
            if self.__locked:
                raise AttributeError("A token is immutable once created")
        
        super().__setattr__(name, value)

    @property
    def name (self):
        return self.token_type.name
    @property
    def value (self):
        return self.position.value
