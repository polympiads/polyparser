
"""
This class represents a range of positions inside a file

  @private __line         the starting line
  @private __column       the starting column
  @private __height       the height of the position range
  @private __last_column  the column on the last line
  @private __render       the associated file reader

  @property line        = __line
  @property column      = __column
  @property height      = __height
  @property last_column = __last_column

Further information is available at : https://polympiads.github.io/polyparser/reference/api/io.html#class-positionrange
"""
class PositionRange:
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
