
import enum

"""
This class represents a token type factory, used to generate the alphabet of token types

Further information is available at : https://polympiads.github.io/polyparser/reference/api/lexer.html#module-factory-class-tokentypefactory
"""
class TokenTypeFactory:
    def __init__ (self, name: str):
        self.name  = name
        self.types = {  }
    def add_token_type (self, name: str):
        self.types[name] = TokenType(self, name)
    def as_enumeration (self):
        return enum.Enum( self.name, self.types )

from polyparser.lexer.token.type import TokenType
