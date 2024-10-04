
from typing import Any, Generic, TypeVar


T = TypeVar("T")

class Optional(Generic[T]):
    __has_object: bool
    __value     : T

    __locked : bool
    def __init__(self, *args) -> None:
        super().__init__()

        self.__has_object = len(args) >= 1
        
        if self.__has_object:
            self.__value = args[0]
        
        self.__locked = True

    @property
    def exists (self):
        return self.__has_object
    @property
    def value (self):
        return self.__value
    
    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, "_Optional__locked"):
            if self.__locked:
                raise AttributeError("Optional objects are immutable")
        
        super().__setattr__(name, value)