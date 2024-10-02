
from typing import Any, Generic, List, Self, Tuple, Type, TypeVar

"""
This class represents an exception for save streams

Further information is available at : https://polympiads.github.io/polyparser/reference/api/io.html#class-savestreamerror
"""
class SaveStreamError(Exception):
    pass

"""
This class represents a saved state for a save stream.

It can be locked and can never be modified again, but this should never be called outside of the module.
You may know whether it is locked by reading the is_locked property.

Further information is available at : https://polympiads.github.io/polyparser/reference/api/io.html#class-savedstate
"""
class SavedState:
    __locked: bool

    def __init__(self) -> None:
        self.__locked = False

    @staticmethod
    def empty (*empty_args) -> Self:
        assert False, "Not implemented in sub class"
    def copy (self, *empty_args) -> Self:
        other = type(self).empty(*empty_args)
        self.copy_into(other)
        return other
    def copy_into (self, other: Self):
        assert False, "Not implemented in sub class"

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, "_SavedState__locked"):
            if self.__locked:
                raise SaveStreamError("SavedState object has been locked")

        super().__setattr__(name, value)

    @property
    def is_locked (self):
        return self.__locked
    def _lock (self): 
        self.__locked = True

T = TypeVar("T", bound=SavedState)

"""
This class represents an atomic modification on a save stream.

The modification can be rolled back once, in which case it locks the state.

The properties bound and old allow you to get the state before modification and current state.

Further information is available at : https://polympiads.github.io/polyparser/reference/api/io.html#class-savestreamatomic-t-extends-savedstate
"""
class SaveStreamAtomic(Generic[T]):
    __bound: T
    __old  : T

    __rollback: bool

    def __init__(self, bound: T, old: T) -> None:
        self.__bound = bound
        self.__old   = old

        self.__rollback = False

    def rollback (self):
        if self.__rollback:
            raise SaveStreamError("Can only rollback an atomic element once")

        self.__bound._lock()

        self.__rollback = True
    @property
    def has_done_rollback (self):
        return self.__rollback

    @property
    def bound(self):
        return self.__bound
    @property
    def old (self):
        return self.__old
    
"""
This class represents a save stream.

It should be instantiated with the type of the saved state and the arguments for the empty static method.

A great example is in the FileReader. You also have access to the with keyboard to get an atomic modification object
With the current state so you can read, modify and rollback.

Further information is available at : https://polympiads.github.io/polyparser/reference/api/io.html#class-savestream-t-extends-savedstate
"""
class SaveStream (Generic[T]):
    __member_class: Type[T]
    __empty_args  : List[Any]

    __atomics: List[SaveStreamAtomic[T]]
    __state  : T

    def __init__(self, member_class: Type[T], *empty_args) -> None:
        super().__init__()

        self.__member_class = member_class
        self.__empty_args   = empty_args

        self.__state = member_class.empty(*empty_args)

        self.__atomics = []

    def __enter__(self) -> Tuple[SaveStreamAtomic[T], T]:
        old_state = self.__state
        if old_state.is_locked:
            raise SaveStreamError("Cannot use with stream when the current with has been rollbacked")

        new_state = self.__state.copy(*self.__empty_args)

        self.__state = new_state
        self.__atomics.append( SaveStreamAtomic(new_state, old_state) )

        return (self.__atomics[-1], new_state)
    def __exit__(self, *args):
        atomic = self.__atomics.pop()

        if not atomic.has_done_rollback:
            atomic.bound.copy_into(atomic.old) # push change to old object if we shouldn't rollback
        self.__state = atomic.old # push last data into current state