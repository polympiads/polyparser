
from polyparser.io.reader import FileReader
from polyparser.lexer     import Lexer
from polyparser.parser    import Parser

class Language:
    __lexer  : Lexer
    __parser : Parser

    def __init__(self):
        self.__lexer  = self.get_lexer  ()
        self.__parser = self.get_parser ()

    def get_lexer (self) -> Lexer:
        raise NotImplementedError()
    def get_parser (self) -> Parser:
        raise NotImplementedError()

    def parse (self, reader: "FileReader"):
        tokens = self.__lexer.try_lexing(reader)

        return self.__parser.try_parsing(tokens)