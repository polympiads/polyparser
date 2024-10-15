
from typing import Any, Dict, List, Tuple
from polyparser.parser.context import ParserContext

def check_context (context: ParserContext, names: List[str], values: Dict[str, Any] = {}):
    for name in names:
        if name in values:
            assert context.get_element(name) == (values[name], True)
        else :
            assert context.get_element(name) == (None, False)

def test_simple_context ():
    context = ParserContext()

    names = [ "abc", "def", "rgb" ]

    check_context(context, names)
    context.set_element( "abc", "Hi !" )
    check_context(context, names, { "abc": "Hi !" })
    context.set_element( "def", "def2" )
    check_context(context, names, { "abc": "Hi !", "def": "def2" })
def test_double_context ():
    context1 = ParserContext()
    context2 = ParserContext(context1)
    
    names = [ "abc", "def", "rgb" ]
    check_context(context2, names)
    check_context(context1, names)
    context2.set_element( "abc", "Hi !" )
    check_context(context2, names, { "abc": "Hi !" })
    check_context(context1, names)
    context1.set_element( "def", "def2" )
    check_context(context2, names, { "abc": "Hi !", "def": "def2" })
    check_context(context1, names, { "def": "def2" })
