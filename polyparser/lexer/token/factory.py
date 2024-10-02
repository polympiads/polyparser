
import enum

class TokenTypeFactory:
    def __init__ (self, name: str):
        self.name  = name
        self.types = {  }
    def add_token_type (self, name: str):
        self.types[name] = TokenType(self, name)
    def as_enumeration (self):
        return enum.Enum( self.name, self.types )

from polyparser.lexer.token.type import TokenType
