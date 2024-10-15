
from polyparser.parser.context import ParserContext
from polyparser.parser.node import ParserNode
from polyparser.parser.primitives.augmented import AugmentedPrimitive, AugmentedType
from polyparser.parser.primitives.token import TokenPrimitive
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream
from tests.parser.primitives.test_primitive_token import MockToken

def test_simple_none ():
    primitive1 = AugmentedPrimitive( TokenPrimitive( "NAME", expects="if" ) )
    primitive2 = AugmentedPrimitive( TokenPrimitive( "EOL", stored=True ) )
    primitive3 = AugmentedPrimitive( TokenPrimitive( "NAME" ) )
    primitive4 = AugmentedPrimitive( TokenPrimitive( "NAME", expects="!if", stored=True ) )

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

def test_simple_optional ():
    primitive1 = AugmentedPrimitive( TokenPrimitive( "NAME", expects="if" ), AugmentedType.OPTIONAL )
    primitive2 = AugmentedPrimitive( TokenPrimitive( "EOL", stored=True ), AugmentedType.OPTIONAL )
    primitive3 = AugmentedPrimitive( TokenPrimitive( "NAME" ), AugmentedType.OPTIONAL )
    primitive4 = AugmentedPrimitive( TokenPrimitive( "NAME", expects="!if", stored=True ), AugmentedType.OPTIONAL )

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

    evaluate( primitive1, ParsingResult.IGNORED, [] )
    evaluate( primitive2, ParsingResult.SUCCESS, [ T[0] ] )
    evaluate( primitive3, ParsingResult.IGNORED, [] )
    evaluate( primitive4, ParsingResult.IGNORED, [] )
    advance()

    evaluate( primitive1, ParsingResult.SUCCESS, [] )
    evaluate( primitive2, ParsingResult.IGNORED, [] )
    evaluate( primitive3, ParsingResult.SUCCESS, [] )
    evaluate( primitive4, ParsingResult.IGNORED, [] )
    advance()
    
    evaluate( primitive1, ParsingResult.IGNORED, [] )
    evaluate( primitive2, ParsingResult.IGNORED, [] )
    evaluate( primitive3, ParsingResult.SUCCESS, [] )
    evaluate( primitive4, ParsingResult.SUCCESS, [ T[2] ] )
    advance()

def test_simple_at_least_one ():
    primitive1 = AugmentedPrimitive( TokenPrimitive( "NAME", stored=True ), augment=AugmentedType.AT_LEAST_ONE )
    primitive2 = AugmentedPrimitive( TokenPrimitive( "EOL",  stored=True ), augment=AugmentedType.AT_LEAST_ONE )

    tokens = [
        MockToken( "NAME", "A" ),
        MockToken( "NAME", "A" ),
        MockToken( "EOL", "A" ),
        MockToken( "EOL", "A" ),
        MockToken( "EOL", "A" ),
        MockToken( "NAME", "A" )
    ]
    stream  = ParserStream(tokens)
    context = ParserContext()

    def check (prim: ParserNode, should_work: bool, res: str, amount: int):
        with stream as (atomic, state):
            result = prim.evaluate(stream, context)
            if should_work: assert result == ParsingResult.SUCCESS
            else : assert result == ParsingResult.FAILED

            args = state.poll_stored()
            assert len(args) == amount
            for i, a in enumerate(args):
                assert a.name == res

    check(primitive2, False, "EOL",  0)
    check(primitive1, True,  "NAME", 2)
    check(primitive1, False, "NAME", 0)
    check(primitive2, True,  "EOL",  3)
    check(primitive2, False, "EOL",  0)
    check(primitive1, True,  "NAME", 1)
    check(primitive1, False, "NAME", 0)
    check(primitive2, False, "EOL",  0)
def test_simple_any_amount ():
    primitive1 = AugmentedPrimitive( TokenPrimitive( "NAME", stored=True ), augment=AugmentedType.ANY_AMOUNT )
    primitive2 = AugmentedPrimitive( TokenPrimitive( "EOL",  stored=True ), augment=AugmentedType.ANY_AMOUNT )

    tokens = [
        MockToken( "NAME", "A" ),
        MockToken( "NAME", "A" ),
        MockToken( "EOL", "A" ),
        MockToken( "EOL", "A" ),
        MockToken( "EOL", "A" ),
        MockToken( "NAME", "A" )
    ]
    stream  = ParserStream(tokens)
    context = ParserContext()

    def check (prim: ParserNode, should_work: bool, res: str, amount: int):
        with stream as (atomic, state):
            result = prim.evaluate(stream, context)
            if should_work: assert result == ParsingResult.SUCCESS
            else : assert result == ParsingResult.IGNORED

            args = state.poll_stored()
            assert len(args) == amount
            for i, a in enumerate(args):
                assert a.name == res

    check(primitive2, False, "EOL",  0)
    check(primitive1, True,  "NAME", 2)
    check(primitive1, False, "NAME", 0)
    check(primitive2, True,  "EOL",  3)
    check(primitive2, False, "EOL",  0)
    check(primitive1, True,  "NAME", 1)
    check(primitive1, False, "NAME", 0)
    check(primitive2, False, "EOL",  0)

def test_prim_type_err ():
    def prim_type__f (*args):
        if args[0].value == "!if":
            raise NotImplementedError()
        else: return args[0]
    prim = AugmentedPrimitive( TokenPrimitive("NAME", True), prim_type=prim_type__f )

    stream = ParserStream([ MockToken("NAME", "if"), MockToken("NAME", "!if") ])
    ctx = ParserContext()

    with stream as (atomic, state):
        assert state.size == 2
        assert prim.evaluate(stream, ctx) == ParsingResult.SUCCESS
        stored = state.poll_stored()
        assert state.size == 1
        assert len(stored) == 1
        assert stored[0].name == "NAME" and stored[0].value == "if"
        assert prim.evaluate(stream, ctx) == ParsingResult.FAILED
        stored = state.poll_stored()
        assert len(stored) == 0
        assert state.size == 1
def test_prim_type_none ():
    def prim_type__f (*args):
        return args
    
    primitive1 = AugmentedPrimitive( TokenPrimitive( "NAME", expects="if" ),               prim_type=prim_type__f )
    primitive2 = AugmentedPrimitive( TokenPrimitive( "EOL", stored=True ),                 prim_type=prim_type__f )
    primitive3 = AugmentedPrimitive( TokenPrimitive( "NAME" ),                             prim_type=prim_type__f )
    primitive4 = AugmentedPrimitive( TokenPrimitive( "NAME", expects="!if", stored=True ), prim_type=prim_type__f )

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

            check_eq([tuple(arr)] if result == ParsingResult.SUCCESS else [])
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

