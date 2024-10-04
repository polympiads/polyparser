
from typing import Dict, Tuple
from polyparser.io.reader import FileReader
from polyparser.lexer.rules.abstract import LexerRule
from polyparser.lexer.token import Token
from polyparser.lexer.token.type import TokenType
from polyparser.utils.optional import Optional

class TokenTypeTrie:
    value: Optional[TokenType]

    nexts: "Dict[str, TokenTypeTrie]"

    def __init__(self) -> None:
        self.value = Optional()
        self.nexts = {}
    
    def has_value (self):
        return self.value.exists
    def get_value (self):
        return self.value.value

    def update (self, name: str, offset: int, value: TokenType):
        if offset == len(name):
            assert not self.value.exists

            self.value = Optional(value)
            return
        
        character = name[offset]
        if character not in self.nexts:
            self.nexts[character] = TokenTypeTrie()
        
        self.nexts[character].update(name, offset + 1, value)
    def find_next (self, character: str) -> "TokenTypeTrie | None":
        if character in self.nexts:
            return self.nexts[character]
        return None

class KeywordLexerRule(LexerRule):
    def __init__(self, keywords: Dict[str, TokenType]) -> None:
        super().__init__()

        self.trie = TokenTypeTrie()

        for key in keywords:
            self.trie.update(key, 0, keywords[key])
    def try_lexing(self, reader: FileReader) -> Optional[Token]:
        param  = None
        offset = 0
        with reader as (atomic, state):
            node = self.trie
            curr = 0

            while node != None and state.size != 0:
                char = state.poll()
                node = node.find_next(char)
                
                if node is None: break

                curr += 1
                if node.has_value():
                    param  = node.get_value()
                    offset = curr

            atomic.rollback()
        
        if param is None: return None

        with reader as (atomic, state):
            for _ in range( offset ):
                state.poll()
        
            return Optional( Token( param, state.as_position() ) )
        