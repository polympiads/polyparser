
from typing import Self

from polyparser.io.savestream import SaveStream, SavedState

"""
This class represents the state of the file reader.
It is represented as an offset in the reader's content

It also allows to generate a position range using the
Initial state and the current state.

Works also as a queue-like object on the characters of the buffer.

Further information is available at : https://polympiads.github.io/polyparser/reference/api/io.html#class-filereaderstate-savedstate
"""
class FileReaderState(SavedState):
    __reader: "FileReader"
    __offset: int

    __is_new : bool

    __start_line   : int
    __start_column : int
    __start_offset : int

    __current_line   : int
    __current_column : int
    
    def __init__(self, reader: "FileReader", offset: int) -> None:
        super().__init__()

        self.__reader = reader
        self.__offset = offset

        self.__current_line   = self.__start_line   = 1
        self.__current_column = self.__start_column = 1

        self.__is_new = True
    
    @staticmethod
    def empty(reader: "FileReader") -> Self:
        return FileReaderState(reader, 0)
    def copy_into(self, other: "FileReaderState"):
        self.__is_new = False
        if other.__is_new:
            other.__is_new = False

            other.__start_line   = self.__current_line
            other.__start_column = self.__current_column
            other.__start_offset = self.__offset
        other.__offset = self.__offset

        other.__current_line   = self.__current_line
        other.__current_column = self.__current_column

    def peek (self):
        return self.__reader.content[self.__offset]
    def poll (self):
        result = self.__reader.content[self.__offset]
        self.__offset += 1

        if result == '\n':
            self.__current_column = 1
            self.__current_line  += 1
        else:
            self.__current_column += 1

        return result
    def as_position (self) -> "PositionRange":
        return PositionRange(
            self.__reader,
            self.__start_line, self.__start_column, 
            self.__current_line   - self.__start_line   + 1,
            self.__current_column,
            self.__start_offset,
            self.__offset - self.__start_offset
        )
    
    @property
    def size (self):
        return max(0, len(self.__reader.content) - self.__offset)
    def __len__(self):
        return self.size

"""
This class represents the file reader as a save stream,
You can instantiate it by passing the path to its constructor,
And you can then retrieve all data using the path and content properties.

You can also use it as a save stream by applying atomic modifications on it.

Further information is available at : https://polympiads.github.io/polyparser/reference/api/io.html#class-filereader-savestream-filereaderstate
"""
class FileReader(SaveStream[FileReaderState]):
    __path    : str
    __content : str

    def __init__(self, path: str, content: str):
        super().__init__( FileReaderState, self )

        self.__path    = path
        self.__content = content
    @staticmethod
    def open (path: str):
        with open(path, "r") as file:
            content = file.read()
            return FileReader(path, content)

    @property
    def content (self):
        return self.__content
    @property
    def path (self):
        return self.__path

from polyparser.io.position import PositionRange