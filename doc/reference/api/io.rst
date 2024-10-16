:tocdepth: 4

.. _`io`:

Input / Output
==============

This page documents the inner API of the ``polyparser.io`` package. It possesses the following interesting modules

#. :ref:`polyparser.io.savestream <polyparser_io_savestream>` - Module responsible for saveable streams
#. :ref:`polyparser.io.reader <polyparser_io_reader>` - Module containing readers
#. :ref:`polyparser.io.position <polyparser_io_position>` - Module containing position utilities

.. _polyparser_io_savestream:

Module ``polyparser.io.savestream``
-----------------------------------

This module gives the guideline for a saveable stream.
The main idea behind this stream is to create an object,
containing a state on which we can read in an atomic way, rolling back in case of an error.

``class SaveStreamError``
~~~~~~~~~~~~~~~~~~~~~~~~~

This class is used to raise an exception in case something goes wrong inside of the stream.

``class SavedState``
~~~~~~~~~~~~~~~~~~~~

This class should be extended and will represent the current state of a stream when it is entered.

static method ``empty(*empty_args)``
""""""""""""""""""""""""""""""""""""

This static method should generate an instance of the type extending ``SavedState`` representing an empty, or default state. If it isn't overwritten, it generates an ``AssertionError``.

method ``copy_into(self, other)``
"""""""""""""""""""""""""""""""""

This method should copy the data from the current instance into the other instance of the type. If it isn't overwritten, it generates an ``AssertionError``.

method ``copy(self, *empty_args)``
""""""""""""""""""""""""""""""""""

This method creates a copy of the current object. If the object was locked, the new one shouldn't be locked. It relies both on ``empty`` and ``copy_into``, and it passes the arguments to ``empty``.

``is_locked``
"""""""""""""

Immutable property represented by a boolean telling whether the object is currently locked. A locked object can't ever be modified again. This happens when the ``_lock`` method is called by another part of the program. This method should never be called outside of the ``savestream`` module as it can lead to damage to the associated atomic modification and to the associated stream.

``class SaveStreamAtomic[T extends SavedState]``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This class contains the necessary data for an atomic modification. It is generated by the ``SaveStream`` when starting a modification.

method ``rollback()``
"""""""""""""""""""""

Cancels the atomic modification and locks the associated data. The program should exit from the modification mode right after rolling back.

``has_done_rollback``
"""""""""""""""""""""

This immutable property allows you to know if the modification has been cancelled.

``bound`` and ``old``
"""""""""""""""""""""

These two immutable properties allow you to get respectively the current state of the stream and the one before the start of the modification.

``class SaveStream[T extends SavedState]``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ``SaveStream`` should be used with the appropriate ``SavedState`` type. One can create such a stream in the following ways :

.. code-block:: python
   :emphasize-lines: 3,6,7,8,10

    # Here, T is the type of your state, and should extend SavedState
    # A simple way to create the stream
    stream = SaveStream[T](T) 

    # Using a custom class
    class CustomStream(SaveStream[T]):
        def __init__(self):
            super().__init__(T)
    
    stream = CustomStream()

Then one can start doing atomic reading on it in the following way :

.. code-block:: python
   :emphasize-lines: 3,6

    # Enter into the stream
    # Returns a tuple containing the atomic modification and the state
    with stream as (atomic, state):
        # You can now read something from the state
        # This is where your custom implementation of SavedState takes place
        something = state.read()

If you want to cancel any modifications that your state has done to your stream, you can do the following

.. code-block:: python
   :emphasize-lines: 7

    # Enter into the stream
    # Returns a tuple containing the atomic modification and the state
    with stream as (atomic, state):
        # Here you read and modify the state ...
        # Something goes wrong and you want to rollback
        # You can then do the following
        atomic.rollback()

        # From this point on, state is locked and can't be used
        # You should leave as soon as possible the with statement
        # As the modification is over.
        
Understanding what happens behind the scenes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The idea is that when you enter in modification mode using the ``with`` keyword,
the stream generates an atomic modification and creates a copy of the current state.
It then outputs both the atomic modification object and the copy. Then you can do some
modifications on the state and leave the modification mode by going out of the statement.

After that, the stream will do the following :

#. If the modification was rollbacked, destroy the current state and replace it by the old one stored in the atomic modification.
#. Otherwise, copy the data of the current state into the old one and put back the old one.

This first idea is somewhat logical as you just destroy all of the old data, but the second can seem strange, but is quite logical if you think of nested modifications.
Once you have finished either modifying or rolling back, the state goes back to the old object so that it is still pointing to the right state, but if there were valid modifications,
then we copy the data into the old state. One can view all the implications in the following code :

.. code-block:: python

    # We will assume that the state contains an index that starts at 0
    with stream as (a1, s1):
        # Here, s1.index = 0, and one can modify it
        s1.index = 1
        with stream as (a2, s2):
            # Here, s1.index = s2.index = 1, but s2 is not s1
            s2.index = 2
            # Now, the values are different and s2.index = 2, s1.index = 1
        # When leaving the with statements, modifications on s2
        # Are propagated to s1 and s1.index = 2
    # Now the modifications on s1 are propagated to the default state
    # And until further modification, any new with statement will start
    # with a state with index 2.

.. _polyparser_io_reader:

Module ``polyparser.io.reader``
-------------------------------

This module contains most notably the ``FileReader`` class, responsible for handling any file reading related computation.
It is an implementation of a SaveStream in the case of characters, where the ``SavedState`` represents a cursor on the list of characters of the file.

``class FileReaderState(SavedState)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This class implements a saved state referencing a file reader.
It works as a queue-like object for the reader, that can be rolled back.
All operations are in ``O(1)`` as it uses always the same string buffer, that is never copied nor
deleted. Only a cursor is used to maintain the start of the buffer of this state.
It inherits all the methods from SavedState, but it also implements the following methods :

method ``peek(self)``
"""""""""""""""""""""

Returns the next character in the buffer

method ``poll(self)``
"""""""""""""""""""""

Removes and returns the next character in the buffer

property ``size`` and ``len(state) = state.__len__(self)``
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

It implements both an immutable ``size`` property and the ``__len__`` method so you can use the ``len`` function on it,
that both contain the size of the remaining buffer.

``class FileReader(SaveStream[FileReaderState])``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This class contains the implementation of a file reader.
It must be instantiated with the path of the file, and you can then access
both the path and content in the immutable properties with the same name.

You can then use it as a ``SaveStream`` where the state is a ``FileReaderState``. For example, if you want to check that the 26 first characters are those of the alphabet, you could do :

.. code-block:: python
   :emphasize-lines: 7

    reader = FileReader("...")

    # Start modification mode
    with reader as (atomic, state):
        is_valid = True
        
        # Poll all the characters and verify them
        for i in range(26):
            if state.poll() != chr(i + ord('a')):
                is_valid = False
                break
        if not is_valid: # if it is invalid, roll back
            atomic.rollback()

.. _polyparser_io_position:

Module ``polyparser.io.position``
---------------------------------

``class PositionRange``
~~~~~~~~~~~~~~~~~~~~~~~

This class represents a position range in a file, associated with the reader.

It is represented as a starting line and starting column in the immutable properties ``line`` and ``column``.
It also contains the height and the ending column in the immutable properties ``height`` and ``last_column``.

.. toctree::
   :hidden:

