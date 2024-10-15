
from typing import Any, List, Self

from polyparser.io.savestream import SavedState

class ParserCursor (SavedState):
    __offset: int
    __stream: "ParserStream"

    __arguments : List[Any]
    __arg_size  : int
    __cur_size  : int

    __new : bool

    def store (self, arg: Any):
        if self.__arg_size == len(self.__arguments):
            self.__arguments.append(arg)
        else:
            self.__arguments[self.__arg_size] = arg
        self.__arg_size += 1
    def poll_stored (self):
        result = self.__arguments[self.__cur_size:self.__arg_size].copy()
        
        self.__arg_size = self.__cur_size
        return result

    def __init__(self, stream: "ParserStream") -> None:
        super().__init__()

        self.__offset = 0
        self.__stream = stream

        self.__arguments = []
        self.__arg_size  = 0
        self.__cur_size  = 0

        self.__new = True

    def __len__ (self):
        return len(self.__stream.tokens) - self.__offset
    @property
    def size (self):
        return len(self)
    
    def peek (self):
        return self.__stream.tokens[self.__offset]
    def poll (self):
        result = self.__stream.tokens[self.__offset]
        self.__offset += 1
        return result

    @staticmethod
    def empty(stream: "ParserStream") -> Self:
        return ParserCursor(stream)
    def copy_into(self, other: Self):
        self.__new = False

        other.__offset = self.__offset
        other.__stream = self.__stream

        other.__arguments = self.__arguments
        other.__arg_size  = self.__arg_size

        if other.__new:
            other.__new = False
            other.__cur_size = self.__arg_size


from polyparser.parser.stream import ParserStream
