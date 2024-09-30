
from typing import Self

from polyparser.io.position import Position
from polyparser.io.savestream import SaveStream, SavedState

class FileReaderState(SavedState):
    __reader: "FileReader"
    __offset: int

    __is_new : bool

    __start_line   : int
    __start_column : int

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
    def as_position (self) -> "Position":
        return Position(
            self.__reader,
            self.__start_line, self.__start_column, 
            self.__current_line   - self.__start_line   + 1,
            self.__current_column )
    
    @property
    def size (self):
        return max(0, len(self.__reader.content) - self.__offset)
    def __len__(self):
        return self.size

class FileReader(SaveStream[FileReaderState]):
    __path    : str
    __content : str

    def __init__(self, path: str):
        super().__init__( FileReaderState, self )

        self.__path = path

        with open(path, "r") as file:
            self.__content = file.read()

    @property
    def content (self):
        return self.__content
    @property
    def path (self):
        return self.__path