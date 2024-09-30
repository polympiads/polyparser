
from typing import Self
from polyparser.io.savestream import *

import pytest

from tests.utils.immutable import check_immutable

def test_saved_state_empty ():
    with pytest.raises(AssertionError):
        SavedState.empty()
def test_saved_state_copy ():
    state = SavedState()
    with pytest.raises(AssertionError):
        state.copy()
def test_saved_state_copy_into ():
    state = SavedState()
    with pytest.raises(AssertionError):
        state.copy_into( SavedState() )
def test_saved_state_lock ():
    state = SavedState()

    state.a = "Hi !"
    state.b = "Hello !"
    check_immutable( state, "is_locked", True )
    assert not state.is_locked

    state._lock()

    check_immutable( state, "a", "Hi 1234 !", SaveStreamError )
    check_immutable( state, "b", "Hello 2 !", SaveStreamError )
    assert state.is_locked

class CTestSavedState(SavedState):
    index: int
    def __init__(self, index: int) -> None:
        super().__init__()
        
        self.index = index

    @staticmethod
    def empty() -> Self:
        return CTestSavedState(0)
    def copy_into(self, other: "CTestSavedState"):
        other.index = self.index

def test_simple_save_stream_modification ():
    stream = SaveStream[CTestSavedState](CTestSavedState)

    with stream as (atomic, state):
        assert atomic.old.index   == 0
        assert atomic.bound.index == 0

        assert state.index == 0
        assert state == atomic.bound
        assert state != atomic.old

        state.index = 1
        assert atomic.bound.index == 1
        assert atomic.old.index   == 0
        assert state.index == 1
    
    assert stream._SaveStream__state.index == 1

    with stream as (atomic, state):
        assert state.index == 1
def test_simple_save_stream_rollback ():
    stream = SaveStream[CTestSavedState](CTestSavedState)

    with stream as (atomic, state):
        state.index = 1

        atomic.rollback()

        assert state.is_locked
    
    with stream as (atomic, state):
        assert state.index == 0
def test_save_stream_double_rollback ():
    stream = SaveStream[CTestSavedState](CTestSavedState)

    with pytest.raises(SaveStreamError):
        with stream as (atomic, state):
            state.index = 1

            atomic.rollback()
            atomic.rollback()
    
    with stream as (atomic, state):
        assert state.index == 0
def test_save_stream_rollback_and_continue ():
    stream = SaveStream[CTestSavedState](CTestSavedState)

    with pytest.raises(SaveStreamError):
        with stream as (atomic, state):
            state.index = 1

            atomic.rollback()
            
            with stream as (atomic2, state2):
                assert False, "Should not reach this statement"
    
    with stream as (atomic, state):
        assert state.index == 0

def test_save_stream_nested_atomics ():
    stream = SaveStream[CTestSavedState](CTestSavedState)

    with stream as (atomic, state):
        with stream as (a2, s2):
            s2.index = 1
            assert s2.index == 1 and state.index == 0
        assert state.index == 1
        
    assert stream._SaveStream__state.index == 1
def test_save_stream_nested_atomics_with_rollback ():
    stream = SaveStream[CTestSavedState](CTestSavedState)

    with stream as (atomic, state):
        with stream as (a2, s2):
            s2.index = 1
            assert s2.index == 1 and state.index == 0
        assert state.index == 1
        atomic.rollback()
        
    assert stream._SaveStream__state.index == 0