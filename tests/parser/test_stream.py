
import pytest
from polyparser.parser.stream import ParserStream


def test_parser_stream ():
    L = [ "a", "b", "c", "d" ]

    stream = ParserStream(L)

    for i in range(len(L)):
        with stream as (atomic, state):    
            assert state.size == len(state) == len(L) - i
            assert L[i] == state.peek()
            assert L[i] == state.poll()
            assert state.size == len(state) == len(L) - i - 1
    
    with stream as (atomic, state):
        with pytest.raises(Exception):
            state.peek()
        with pytest.raises(Exception):
            state.poll()

def test_parser_stream_arglist ():
    L = [ "a", "b", "c", "d" ]

    stream = ParserStream(L)

    with stream as (atomic1, state1):
        state1.store( "H" )

        with stream as (atomic2, state2):
            state2.store("ello")
            data = state2.poll_stored()

            state2.store("ello, World !")
            assert data == [ "ello" ]

        assert state1.poll_stored() == [ "H", "ello, World !" ]

def test_parser_stream_arglist_rollback ():
    L = [ "a", "b", "c", "d" ]

    stream = ParserStream(L)

    with stream as (atomic1, state1):
        state1.store( "H" )

        with stream as (atomic2, state2):
            state2.store("ello")
            atomic2.rollback()

        with stream as (atomic2, state2):
            state2.store("ello, World !")
        
        assert state1.poll_stored() == [ "H", "ello, World !" ]
