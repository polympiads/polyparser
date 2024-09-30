
class Position:
    __line   : int
    __column : int

    __height : int
    __last_column : int

    __reader : "FileReader"

    def __init__(self, reader: "FileReader", line: int, column: int, height: int, last_column: int):
        self.__reader = reader

        self.__line   = line
        self.__column = column
        
        self.__height = height
        self.__last_column = last_column

    @property
    def line (self):
        return self.__line
    @property
    def column (self):
        return self.__column
    @property
    def last_column (self):
        return self.__last_column
    @property
    def height (self):
        return self.__height

from polyparser.io.reader import FileReader
