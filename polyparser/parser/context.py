
from typing import Any, Dict, Tuple

class ParserContext:
    __next : "ParserContext | None"
    __ctx  : Dict[str, Any]

    def __init__(self, next: "ParserContext | None" = None) -> None:
        self.__next = next
        self.__ctx  = {}
    
    def is_in_current (self, name: str):
        return name in self.__ctx
    def get_element (self, name: str) -> Tuple[Any, bool]:
        if self.is_in_current(name):
            return (self.__ctx[name], True)
        if self.__next is not None:
            return self.__next.get_element(name)
        return (None, False)
    def set_element (self, name: str, value: Any):
        self.__ctx[name] = value
