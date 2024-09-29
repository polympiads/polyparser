
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from polyparser.io.reader import FileReader

class Position:
    __line   : int
    __column : int

    __height : int
    __width  : int

    __reader : "FileReader"

    def __init__(self, reader: "FileReader", line: int, column: int, height: int, width: int):
        self.__reader = reader

        self.__line   = line
        self.__column = column
        
        self.__height = height
        self.__width  = width

    @property
    def line (self):
        return self.__line
    @property
    def column (self):
        return self.__column
    @property
    def width (self):
        return self.__width
    @property
    def height (self):
        return self.__height
