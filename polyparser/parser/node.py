
from polyparser.parser.context import ParserContext
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream

class ParserNode:
    def evaluate (self, stream: ParserStream, context: "ParserContext") -> ParsingResult:
        raise NotImplementedError()
