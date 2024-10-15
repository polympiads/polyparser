
from polyparser.parser.context import ParserContext
from polyparser.parser.primitives.token import TokenPrimitive
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream

class MockToken:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

def test_is_valid_primitive ():
    primitive = TokenPrimitive( "if" )

    assert     primitive.is_valid( MockToken( "if", "if(expr) {}" ) )
    assert not primitive.is_valid( MockToken( "!if", "if(expr) {}" ) )

    primitive = TokenPrimitive( "if", expects="if(expr) {}" )
    
    assert     primitive.is_valid( MockToken( "if", "if(expr) {}" ) )
    assert not primitive.is_valid( MockToken( "!if", "if(expr) {}" ) )
    assert not primitive.is_valid( MockToken( "if", "if(expr2) {}" ) )
def test_primitive ():
    primitive1 = TokenPrimitive( "NAME", expects="if" )
    primitive2 = TokenPrimitive( "EOL", stored=True )
    primitive3 = TokenPrimitive( "NAME" )
    primitive4 = TokenPrimitive( "NAME", expects="!if", stored=True )

    T = [ MockToken("EOL", "\n"), MockToken("NAME", "if"), MockToken("NAME", "!if") ]
    context = ParserContext()
    stream  = ParserStream(T)

    def check_eq (arr):
        with stream as (atomic, state):
            args = state._ParserCursor__arguments
            size = state._ParserCursor__arg_size

            assert size == len(arr)
            assert args[:size] == arr
    def evaluate (prim: TokenPrimitive, result: ParsingResult, arr, rollback = True):
        with stream as (atomic, state):
            assert prim.evaluate(stream, context) == result

            check_eq(arr)
            if rollback: atomic.rollback()
    def advance ():
        with stream as (atomic, state):
            state.poll()

    evaluate( primitive1, ParsingResult.FAILED,  [] )
    evaluate( primitive2, ParsingResult.SUCCESS, [ T[0] ] )
    evaluate( primitive3, ParsingResult.FAILED,  [] )
    evaluate( primitive4, ParsingResult.FAILED,  [] )
    advance()

    evaluate( primitive1, ParsingResult.SUCCESS, [] )
    evaluate( primitive2, ParsingResult.FAILED,  [] )
    evaluate( primitive3, ParsingResult.SUCCESS, [] )
    evaluate( primitive4, ParsingResult.FAILED,  [] )
    advance()
    
    evaluate( primitive1, ParsingResult.FAILED,  [] )
    evaluate( primitive2, ParsingResult.FAILED,  [] )
    evaluate( primitive3, ParsingResult.SUCCESS, [] )
    evaluate( primitive4, ParsingResult.SUCCESS, [ T[2] ] )
    advance()

