
from ast import Tuple
from typing import List
from polyparser.io.reader import FileReader
from polyparser.languages.language import PolyLanguage
from polyparser.lexer import Lexer
from polyparser.parser.context import ParserContext
from polyparser.parser.node import BoundNode, ParserNode
from polyparser.parser.primitives.augmented import AugmentedPrimitive, AugmentedType
from polyparser.parser.primitives.branch import OrPrimitive
from polyparser.parser.primitives.call import CallPrimitive
from polyparser.parser.primitives.function import FunctionNode
from polyparser.parser.primitives.list import ListPrimitive
from polyparser.parser.primitives.token import TokenPrimitive
from polyparser.parser.result import ParsingResult
from polyparser.parser.stream import ParserStream

POLY_LANGUAGE_SCRIPT = """
def token_primitive(a, b)(c): TokenPrimitive =
    /SLASH/ ?//SLASH/ //NAME/ ?[/DOT/ //STRING/]^Aug | */SLASH/
"""

POLY_LANGUAGE_TOKENS = [
    # def token_primitive: TokenPrimitive =
    ("DEFINE", "def"), ("NAME", "token_primitive"), 
    ("L_B", "("), ("NAME", "a"), ("COMMA", ","), ("NAME", "b"), ("R_B", ")"),
    ("L_B", "("), ("NAME", "c"), ("R_B", ")"),
    ("TWODOTS", ":"), ("NAME", "TokenPrimitive"), ("EQUALS", "="),
    ("INDENT",  "    "),

    # /SLASH/
    ("DASH", "/"), ("NAME", "SLASH"), ("DASH", "/"),

    # ?//SLASH/
    ("QMARK", "?"), ("DASH", "/"), ("DASH", "/"), ("NAME", "SLASH"), ("DASH", "/"),

    # //NAME/
    ("DASH", "/"), ("DASH", "/"), ("NAME", "NAME"), ("DASH", "/"),
    
    # ?[/DOT/ //STRING/]
    ("QMARK", "?"), ("L_SQ_B", "["), ("DASH", "/"), ("NAME", "DOT"), ("DASH", "/"),
    ("DASH", "/"), ("DASH", "/"), ("NAME", "STRING"), ("DASH", "/"), ("R_SQ_B", "]"),
    ("HAT", "^"), ("NAME", "Aug"), ("PIPE", "|"), ("STAR", "*"),
    
    # /SLASH/
    ("DASH", "/"), ("NAME", "SLASH"), ("DASH", "/"),
]

def test_poly_language_lexer ():
    reader = FileReader(
        "<lang>",
        POLY_LANGUAGE_SCRIPT
    )

    lang = PolyLanguage()
    lexr = lang.get_lexer()
    
    tokens = lexr.try_lexing( reader )

    results = POLY_LANGUAGE_TOKENS
    for index, token in enumerate(tokens):
        assert token.name  == results[index][0]
        assert token.value == results[index][1]

def wrap_runner (lexr: Lexer, prsr: ParserNode, augments = {}):
    def run (string: str, args: List | None = None, expects: ParsingResult | None = None):
        reader = FileReader("<lang>", string)
        tokens = lexr.try_lexing(reader)

        stream  = ParserStream( tokens )
        context = PolyLanguage(augments).get_parser().get_context()
        
        with stream as (atomic, state):
            if args is None:
                result = prsr.evaluate( stream, context )
            else:
                result = prsr.call( stream, context, args )
            if expects is not None:
                assert result == expects

            return state.poll_stored()
    return run    

def readable_context (ctx: ParserContext):
    dct = ctx._ParserContext__ctx
    return { o: as_readable(dct[o], True) for o in dct.keys() }
def as_readable (node: ParserNode, can_be_anything = False):
    if isinstance(node, list) and len(node) == 1: node = node[0]
    if can_be_anything and not isinstance(node, ParserNode):
        return node
    assert isinstance(node, ParserNode)
    if isinstance(node, BoundNode):
        return (as_readable(node._BoundNode__sub_node), readable_context(node._BoundNode__context))
    if isinstance(node, TokenPrimitive):
        return (node._TokenPrimitive__name, node._TokenPrimitive__stored, node._TokenPrimitive__expects)
    if isinstance(node, ListPrimitive):
        return list(map(as_readable, node._ListPrimitive__primitives))
    if isinstance(node, CallPrimitive):
        return (node._CallPrimitive__name, list(map(as_readable, node._CallPrimitive__args)))
    if isinstance(node, OrPrimitive):
        return tuple(map(as_readable, node._OrPrimitive__primitives))
    if isinstance(node, AugmentedPrimitive):
        return (as_readable( node._AugmentedPrimitive__sub_primitive ), node._AugmentedPrimitive__augment, node._AugmentedPrimitive__prim_type)
    if isinstance (node, FunctionNode):
        return (node._FunctionNode__name, node._FunctionNode__args_names, as_readable( node._FunctionNode__target ))
def verify_equality (node: ParserNode, data):
    if isinstance(node, list) and len(node) == 1: node = node[0]
    assert isinstance(node, ParserNode)
    def verify_helper (n: ParserNode, d):
        if isinstance(n, TokenPrimitive):
            type, stored, expects = d
            assert n._TokenPrimitive__name    == type
            assert n._TokenPrimitive__stored  == stored
            assert n._TokenPrimitive__expects == expects
        if isinstance(n, ListPrimitive):
            assert isinstance(d, list)

            assert len(n._ListPrimitive__primitives) == len(d)
            for prim, _d in zip(n._ListPrimitive__primitives, d):
                verify_helper(prim, _d)
        if isinstance(n, OrPrimitive):
            assert isinstance(d, tuple)

            assert len(n._OrPrimitive__primitives) == len(d)
            for prim, _d in zip(n._OrPrimitive__primitives, d):
                verify_helper(prim, _d)
        if isinstance(n, CallPrimitive):
            name, args = d
            assert n._CallPrimitive__name == name

            assert len(n._CallPrimitive__args) == len(args)

            for prim, _d in zip(n._CallPrimitive__args, args):
                verify_helper(prim, _d)
        if isinstance(n, AugmentedPrimitive):
            subp, aug, typ = d

            verify_helper( n._AugmentedPrimitive__sub_primitive, subp )
            assert n._AugmentedPrimitive__augment == aug
            assert n._AugmentedPrimitive__prim_type == typ
    
    verify_helper(node, data)
def test_poly_language_token_parser ():
    lang = PolyLanguage()
    lexr = lang.get_lexer ()
    prsr = lang.token_parser ()

    run = wrap_runner(lexr, prsr)

    def is_same (prim: "Tuple[TokenPrimitive]", type: str, stored = False, expects = None):
        prim = prim[0]
        
        verify_equality(prim, (type, stored, expects))

    is_same( run( "/DASH/" ),  "DASH" )
    is_same( run( "//DASH/" ), "DASH", True )
    is_same( run( "//NAME:\"if\"/" ), "NAME", True, "if" )
    is_same( run( "/NAME:\"if\"/" ), "NAME", False, "if" )

def test_poly_language_simple_call_parser ():
    lang = PolyLanguage()
    lexr = lang.get_lexer ()
    prsr = lang.call_parser ()

    run = wrap_runner(lexr, prsr)

    verify_equality( run("func")[0], ("func", []) )
def test_poly_language_simple_primitive ():
    lang = PolyLanguage()
    lexr = lang.get_lexer ()
    for prsr in [ lang.simple_primitive_parser(), lang.primitive_parser() ]:
        prsr = lang.simple_primitive_parser ()

        run = wrap_runner(lexr, prsr)

        verify_equality( run( "/DASH/" ),         ("DASH", False, None) )
        verify_equality( run( "//DASH/" ),        ("DASH", True,  None) )
        verify_equality( run( "//NAME:\"if\"/" ), ("NAME", True,  "if") )
        verify_equality( run( "/NAME:\"if\"/" ),  ("NAME", False, "if") )

        verify_equality( run( "func" ),  ("func", []) )
        
        verify_equality( run( "[func [/L_B/ //NAME/ /R_B/]]" ), [
            ("func", []),
            [
                ("L_B", False, None),
                ("NAME", True, None),
                ("R_B", False, None)
            ]
        ] )

def test_poly_language_list_primitive ():
    lang = PolyLanguage()
    lexr = lang.get_lexer()
    prsr = lang.list_primitive_parser()

    run = wrap_runner(lexr, prsr)

    verify_equality( run("[]"), [] )
    verify_equality( run("[/DASH/]"), [("DASH", False, None)] )
    verify_equality(
        run("[/SLASH/ //NAME/ /SLASH/]"),
        [ ("SLASH", False, None), ("NAME", True, None), ("SLASH", False, None) ] )
    verify_equality(
        run("[/L_SQ_B:\"[\"/ func //R_SQ_B:\"]\"/]"),
        [ ("L_SQ_B", False, "["), ("func", []), ("R_SQ_B", True, "]") ] )

def test_poly_language_augmented_primitive ():
    def a(): return None
    def b(): return None
    lang = PolyLanguage({ "a": a, "b": b })
    lexr = lang.get_lexer()
    prsr = lang.augmented_primitive_parser()

    run = wrap_runner(lexr, prsr, { "a": a, "b": b })

    verify_equality( run(" /DASH/"),  ( "DASH", False, None ) )
    verify_equality( run("?/DASH/"), (( "DASH", False, None ), AugmentedType.OPTIONAL,     None) )
    verify_equality( run("*/DASH/"), (( "DASH", False, None ), AugmentedType.ANY_AMOUNT,   None) )
    verify_equality( run("+/DASH/"), (( "DASH", False, None ), AugmentedType.AT_LEAST_ONE, None) )
    verify_equality( run(" /DASH/^a"), (( "DASH", False, None ), None,                       a ) )
    verify_equality( run("?/DASH/^a"), (( "DASH", False, None ), AugmentedType.OPTIONAL,     a) )
    verify_equality( run("*/DASH/^a"), (( "DASH", False, None ), AugmentedType.ANY_AMOUNT,   a) )
    verify_equality( run("+/DASH/^a"), (( "DASH", False, None ), AugmentedType.AT_LEAST_ONE, a) )
    verify_equality( run(" [/DASH/^b]"),  [(( "DASH", False, None ), None, b)])
    verify_equality( run("?[/DASH/^b]"), ([(( "DASH", False, None ), None, b)], AugmentedType.OPTIONAL,     None) )
    verify_equality( run("*[/DASH/^b]"), ([(( "DASH", False, None ), None, b)], AugmentedType.ANY_AMOUNT,   None) )
    verify_equality( run("+[/DASH/^b]"), ([(( "DASH", False, None ), None, b)], AugmentedType.AT_LEAST_ONE, None) )
def test_poly_language_or_primitive ():
    def a(): return None
    def b(): return None
    lang = PolyLanguage({ "a": a, "b": b })
    lexr = lang.get_lexer()
    prsr = lang.or_primitive_parser()

    run = wrap_runner(lexr, prsr, { "a": a, "b": b })

    verify_equality( run("//DASH/"), ("DASH", True, None) )
    verify_equality( run("//DASH/ | //SLASH/"), (("DASH", True, None), ("SLASH", True, None)) )
    verify_equality( run("//DASH/ | ?//SLASH/^a"), (("DASH", True, None), (("SLASH", True, None), AugmentedType.OPTIONAL, a)) )
    verify_equality( run("//DASH/ | [//DASH/ | //DASH/]"),
        (("DASH", True, None), [(("DASH", True, None), ("DASH", True, None))]) )

def test_poly_language_call_one_argument ():
    def a(): return None
    def b(): return None
    lang = PolyLanguage({ "a": a, "b": b })
    lexr = lang.get_lexer()
    prsr = lang.or_primitive_parser()

    run = wrap_runner(lexr, prsr, { "a": a, "b": b })

    verify_equality( run("function(indent)"), ('function', [[('indent', [])]]) )
    verify_equality( run( "function(indent /INDENTATION/)" ),
        ('function', [[('indent', []), ('INDENTATION', False, None)]]) )
def test_poly_language_call_mutli_argument ():
    def a(): return None
    def b(): return None

    lang = PolyLanguage({ "a": a, "b": b })
    lexr = lang.get_lexer()
    prsr = lang.or_primitive_parser()

    run = wrap_runner(lexr, prsr, { "a": a, "b": b })

    verify_equality(run("f(x y, z)([r(//G/)] | //H/)"), (
        'f',
        [
            [('x', []), ('y', [])], 
            [('z', [])], 
            [
                (
                    [
                        (
                            'r', 
                            [
                                [('G', True, None)]
                            ]
                        )
                    ], 
                    ('H', True, None)
                )
            ]
        ]
    ))

def test_poly_language_block ():
    def a(): return None
    def b(): return None

    lang = PolyLanguage({ "a": a, "b": b })
    lexr = lang.get_lexer()
    prsr = lang.block_parser()

    run = wrap_runner(lexr, prsr, { "a": a, "b": b })

    indentation = TokenPrimitive( "INDENT" )
    verify_equality(
        run( "\n\tname f(h^b)\n\t//G/", [ indentation ] ),
        [
            ('name', []), 
            ('f', [[ (('h', []), None, b) ]]), 
            ('G', True, None)
        ]
    )
    
    run( "a", [ indentation ], ParsingResult.FAILED )
    prsr = lang.block_parser(True)

    run = wrap_runner(lexr, prsr, { "a": a, "b": b })

    indentation = TokenPrimitive( "INDENT" )
    assert run( "a", [ indentation ], ParsingResult.IGNORED ) == []
    verify_equality( run( "a", [ ListPrimitive() ], ParsingResult.SUCCESS ), [ ("a", []) ] )

def test_poly_language_function ():
    def a(): return None
    def b(): return None

    lang = PolyLanguage({ "a": a, "b": b })
    lexr = lang.get_lexer()
    prsr = lang.function_parser()
    
    run = wrap_runner(lexr, prsr, { "a": a, "b": b })

    verify_equality( run("\ndef f = \n\tname", [ ListPrimitive() ]), ('f', [], [('name', [])]) )
    verify_equality( run("\n\tdef f = \n\t\tname", [ TokenPrimitive("INDENT") ]), ('f', [], [('name', [])]) )
    verify_equality( run("def f(x, z)(y) =\n\tname", [ ListPrimitive() ] ), ('f', ['x', 'z', 'y'], [('name', [])]) )
    verify_equality( run("def f: a =\n\tname", [ ListPrimitive() ]),
        ('f', [], ([('name', [])], None, a) ) )
    verify_equality( run("def f(x, z)(y): a =\n\tname", [ ListPrimitive() ]),
        ('f', ['x', 'z', 'y'], ([('name', [])], None, a)) )

    verify_equality(
        run("def f(x, z): a =\n\tdef g(y) =\n\t\tname", [ ListPrimitive() ]),
        (
            'f', ['x', 'z'], 
            (
                [('g', ['y'], [('name', [])])], 
                None,
                a
            )
        )
    )

def test_poly_language_primitives ():
    lang = PolyLanguage({ 
        "TokenPrimitive"     : "TokenPrimitive",
        "CallPrimitive"      : "CallPrimitive",
        "ListPrimitive"      : "ListPrimitive",
        "OrPrimitive"        : "OrPrimitive",
        "AugmentedPrimitive" : "AugmentedPrimitive"
    })
    lexr = lang.get_lexer()
    prsr = lang.get_parser()

    def run (s: str):
        return prsr.try_parsing( lexr.try_lexing(FileReader("<lang>", s)) )

    verify_equality(
        run("[/SLASH/ ?//SLASH/ //NAME/ ?[//TWODOTS/ //STRING/] /SLASH/]^TokenPrimitive"),
        [
            (
                [
                    ("SLASH", False, None),
                    (("SLASH", True, None), AugmentedType.OPTIONAL, None),
                    ("NAME", True, None),
                    ([ ("TWODOTS", True, None), ("STRING", True, None) ], AugmentedType.OPTIONAL, None),
                    ("SLASH", False, None)
                ],
                None,
                "TokenPrimitive"
            )
        ]
    )
    verify_equality(
        run("[/L_SQ_B/ *primitive /R_SQ_B/]^ListPrimitive"),
        [
            (
                [
                    ("L_SQ_B", False, None),
                    (("primitive", []), AugmentedType.ANY_AMOUNT, None),
                    ("R_SQ_B", False, None)
                ],
                None,
                "ListPrimitive"
            )
        ]
    )
    verify_equality(
        run("token_primitive | call_primitive | list_primitive"),
        [(
            ( "token_primitive", [] ),
            ( "call_primitive",  [] ),
            ( "list_primitive",  [] )
        )]
    )
    verify_equality(
        run("[?[//QMARK/ | //PLUS/ | //STAR/] simple_primitive ?[//BIND/ //NAME/]]^AugmentedPrimitive"),
        [(
            [
                ([ (("QMARK", True, None), ("PLUS", True, None), ("STAR", True, None)) ], AugmentedType.OPTIONAL, None),
                ("simple_primitive", []),
                ([ ("BIND", True, None), ("NAME", True, None) ], AugmentedType.OPTIONAL, None)
            ],
            None,
            "AugmentedPrimitive"
        )]
    )

    verify_equality(
        run("[augmented_primitive *[/OR/ augmented_primitive]]^OrPrimitive"),
        [(
            [
                ('augmented_primitive', []), 
                (
                    [('OR', False, None), ('augmented_primitive', [])],
                    AugmentedType.ANY_AMOUNT,
                    None
                )
            ], 
            None, 
            'OrPrimitive'
        )]
    )


POLY_LANGUAGE_IN_POLY_LANGUAGE = """
def token_primitive: TokenPrimitive =
    /SLASH/ ?//SLASH/ //NAME/ ?[//TWODOTS/ //STRING/] /SLASH/

def list_primitive: ListPrimitive =
    /L_SQ_B/ *primitive /R_SQ_B/

def call_primitive: CallPrimitive =
    //NAME/ *[/L_B/ primitive *[/COMMA/ primitive] /R_B/]

def simple_primitive =
    token_primitive | call_primitive | list_primitive
def augmented_primitive: AugmentedPrimitive =
    ?[//QMARK/ | //PLUS/ | //STAR/]
    simple_primitive
    ?[//BIND/ //NAME/] 

def or_primitive: OrPrimitive =
    augmented_primitive *[/PIPE/ augmented_primitive]
def primitive =
    or_primitive

def block(indent): ListPrimitive =
    +[[indent +primitive] | function(indent)] 

def function(indent): Function =
    indent 
    /DEFINE/ //NAME/
    *[/L_B/ //NAME/ *[/COMMA/ //NAME/] /R_B/]
    ?[//HAT/ //NAME/]
    /EQUALS/
    block(indent /INDENTATION/)

def main =
    block([]) 
"""
POLY_LANGUAGE_REPRESENTATION = [
    (
        'token_primitive', [], 
        (
            [
                ('SLASH', False, None), (('SLASH', True, None), AugmentedType.OPTIONAL, None), 
                ('NAME', True, None), ([('TWODOTS', True, None), ('STRING', True, None)], AugmentedType.OPTIONAL, None),
                ('SLASH', False, None)
            ], 
            None, 
            'TokenPrimitive'
        )
    ), 
    (
        'list_primitive', [], 
        (
            [
                ('L_SQ_B', False, None), (('primitive', []), AugmentedType.ANY_AMOUNT, None), ('R_SQ_B', False, None)
            ], 
            None,
            'ListPrimitive'
        )
    ), 
    (
        'call_primitive', [], 
        (
            [
                ('NAME', True, None), 
                (
                    [
                        ('L_B', False, None), 
                        ('primitive', []), 
                        (
                            [('COMMA', False, None), ('primitive', [])], 
                            AugmentedType.ANY_AMOUNT,
                            None
                        ), 
                        ('R_B', False, None)
                    ], 
                    AugmentedType.ANY_AMOUNT, 
                    None
                )
            ], 
            None,
            'CallPrimitive'
        )
    ), 
    (
        'simple_primitive', [], 
        [
            (('token_primitive', []), ('call_primitive', []), ('list_primitive', []))
        ]
    ), 
    (
        'augmented_primitive', [], 
        (
            [
                (
                    [
                        (('QMARK', True, None), ('PLUS', True, None), ('STAR', True, None))
                    ], 
                    AugmentedType.OPTIONAL,
                    None
                ), 
                ('simple_primitive', []), 
                ([('BIND', True, None), ('NAME', True, None)], AugmentedType.OPTIONAL, None)
            ], 
            None,
            'AugmentedPrimitive'
        )
    ), 
    (
        'or_primitive', [], 
        (
            [
                ('augmented_primitive', []), 
                ([('OR', False, None), ('augmented_primitive', [])], AugmentedType.ANY_AMOUNT, None)
            ], 
            None,
            'OrPrimitive'
        )
    ),
    ('primitive', [], [('or_primitive', [])]),
    (
        'block', ['indent'], 
        (
            [
                (
                    [
                        (
                            [
                                ('indent', []),
                                (('primitive', []), AugmentedType.AT_LEAST_ONE, None)
                            ],
                            ('function', [[('indent', [])]])
                        )
                    ],
                    AugmentedType.AT_LEAST_ONE,
                    None
                )
            ],
            None,
            'ListPrimitive'
        )
    ), 
    (
        'function', ['indent'], 
        (
            [
                ('indent', []), ('DEFINE', False, None), ('NAME', True, None), 
                (
                    [
                        (
                            [
                                ('L_B', False, None),
                                ([('NAME', True, None)], AugmentedType.OPTIONAL, None),
                                ('R_B', False, None)
                            ],
                            AugmentedType.ANY_AMOUNT,
                            None
                        )
                    ], 
                    AugmentedType.ANY_AMOUNT, 
                    None
                ), 
                ('EQUALS', False, None),
                ('block', [[('indent', []), ('INDENTATION', False, None)]])
            ], 
            None,
            'Function'
        )
    ),
    ('main', [], [('block', [[]])])
]

def test_poly_language_full ():
    language = PolyLanguage({ 
        "TokenPrimitive"     : "TokenPrimitive",
        "CallPrimitive"      : "CallPrimitive",
        "ListPrimitive"      : "ListPrimitive",
        "OrPrimitive"        : "OrPrimitive",
        "AugmentedPrimitive" : "AugmentedPrimitive",
        "Function"           : "Function"
    })
    result = language.parse( FileReader("polylanguage", POLY_LANGUAGE_IN_POLY_LANGUAGE) )

    verify_equality(result, POLY_LANGUAGE_REPRESENTATION)