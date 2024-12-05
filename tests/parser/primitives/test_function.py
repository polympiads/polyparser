
import pytest
from polyparser.parser.context import ParserContext
from polyparser.parser.node import BoundNode, ParserNode
from polyparser.parser.primitives.call import CallPrimitive
from polyparser.parser.primitives.function import FunctionNode
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream

def test_simple_function ():
    gcontext = ParserContext()
    gcontext.set_element( "name1", "value" )
    vstream = ParserStream([])

    class T (ParserNode):
        visit = 0
        def __init__(self, res):
            self.res = res
        def evaluate(self, stream: ParserStream, context: ParserContext) -> ParsingResult:
            self.visit += 1

            assert context != gcontext
            assert context.get_element("name1") == ("value", True)
            assert context.get_element("name2") == (None, False)
            assert stream == vstream
            return self.res

    succ = T( ParsingResult.SUCCESS ); FunctionNode( "succ", succ, [] ).evaluate( vstream, gcontext )
    fail = T( ParsingResult.FAILED  ); FunctionNode( "fail", fail, [] ).evaluate( vstream, gcontext )
    ignr = T( ParsingResult.IGNORED ); FunctionNode( "ignr", ignr, [] ).evaluate( vstream, gcontext )

    def check (name: str):
        value, exists = gcontext.get_element(name)
        assert exists
        assert isinstance(value, BoundNode)
    check("succ")
    check("fail")
    check("ignr")

    assert CallPrimitive( "succ" ).evaluate( vstream, gcontext ) == ParsingResult.SUCCESS
    assert CallPrimitive( "succ" ).evaluate( vstream, gcontext ) == ParsingResult.SUCCESS
    assert CallPrimitive( "fail" ).evaluate( vstream, gcontext ) == ParsingResult.FAILED
    assert CallPrimitive( "ignr" ).evaluate( vstream, gcontext ) == ParsingResult.IGNORED

    assert succ.visit == 2
    assert fail.visit == 1
    assert ignr.visit == 1

    with pytest.raises(NotImplementedError, match="Argument count for method 'succ' is wrong, expected 0 got 1."):
        assert CallPrimitive( "succ", "arg1" ).evaluate( vstream, gcontext ) == ParsingResult.SUCCESS

def test_function_with_arguments ():
    gcontext = ParserContext()
    gcontext.set_element( "name1", "value" )
    vstream = ParserStream([])

    class T (ParserNode):
        visit = 0
        def __init__(self, res):
            self.res = res
        def call(self, stream: ParserStream, context: ParserContext, arguments) -> ParsingResult:
            assert arguments == []
            self.visit += 1

            assert context == gcontext
            assert context.get_element("name1") == ("value", True)
            assert context.get_element("name2") == (None, False)
            assert stream == vstream
            return self.res
        
    func = FunctionNode("func", CallPrimitive("target"), [ "target" ])
    func.evaluate( vstream, gcontext )

    succ = T( ParsingResult.SUCCESS )
    fail = T( ParsingResult.FAILED  )
    ignr = T( ParsingResult.IGNORED )

    def check (name: str):
        value, exists = gcontext.get_element(name)
        assert exists
        assert isinstance(value, BoundNode)
    check("func")

    assert CallPrimitive( "func", succ ).evaluate( vstream, gcontext ) == ParsingResult.SUCCESS
    assert CallPrimitive( "func", succ ).evaluate( vstream, gcontext ) == ParsingResult.SUCCESS
    assert CallPrimitive( "func", fail ).evaluate( vstream, gcontext ) == ParsingResult.FAILED
    assert CallPrimitive( "func", ignr ).evaluate( vstream, gcontext ) == ParsingResult.IGNORED

    assert succ.visit == 2
    assert fail.visit == 1
    assert ignr.visit == 1

    with pytest.raises(NotImplementedError, match="Argument count for method 'func' is wrong, expected 1 got 0."):
        assert CallPrimitive( "func" ).evaluate( vstream, gcontext ) == ParsingResult.SUCCESS
    with pytest.raises(NotImplementedError, match="Argument count for method 'func' is wrong, expected 1 got 2."):
        assert CallPrimitive( "func", succ, fail ).evaluate( vstream, gcontext ) == ParsingResult.SUCCESS

def test_higher_order_function ():
    gcontext = ParserContext()
    gcontext.set_element( "name1", "value" )
    vstream = ParserStream([])

    class T(ParserNode):
        visit = 0
        def __init__(self, res):
            self.res = res
        def call(self, stream: ParserStream, context: ParserContext, arguments) -> ParsingResult:
            assert arguments == []
            self.visit += 1

            assert context == gcontext
            assert context.get_element("name1") == ("value", True)
            assert context.get_element("name2") == (None, False)
            assert stream == vstream
            return self.res
    
    #
    # def func2 (target, target2) =
    #     target(target2)
    # def func (target) =
    #     target()
    # 
    # // Run the following program
    # func2(func, T)
    #

    func = FunctionNode("func", CallPrimitive("target"), [ "target" ])
    func.evaluate( vstream, gcontext )
    func2 = FunctionNode("func2", CallPrimitive("target", CallPrimitive("target2")), [ "target", "target2" ])
    func2.evaluate( vstream, gcontext )

    value = T(ParsingResult.SUCCESS)
    assert CallPrimitive( "func2", CallPrimitive("func"), value ).evaluate( vstream, gcontext )
    assert value.visit == 1
