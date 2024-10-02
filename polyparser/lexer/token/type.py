
from typing import TYPE_CHECKING, Any

class TokenType:
    factory: "TokenTypeFactory"

    name: str

    __locked: bool

    def __init__(self, factory: "TokenTypeFactory", name: str) -> None:
        self.factory = factory
        
        self.name = name

        self.__locked = True
    
    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, "_TokenType__locked"):
            if self.__locked:
                raise AttributeError("Token types are immutable")
        
        super().__setattr__(name, value)

from polyparser.lexer.token.factory import TokenTypeFactory
