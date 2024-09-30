
import random
import pytest
from polyparser.io.reader import FileReader
from tests.utils.immutable import check_immutable

PATHS = [ "tests/io/file_tests/01.txt", "tests/io/file_tests/02.txt", "tests/io/file_tests/03.txt" ]

def test_simple_reader ():
    PATH    = PATHS[0]
    CONTENT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi. Proin porttitor, orci nec nonummy molestie, enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper. Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim. Pellentesque congue. Ut in risus volutpat libero pharetra tempor. Cras vestibulum bibendum augue. Praesent egestas leo in pede. Praesent blandit odio eu enim. Pellentesque sed dui ut augue blandit sodales. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Aliquam nibh. Mauris ac mauris sed pede pellentesque fermentum. Maecenas adipiscing ante non diam sodales hendrerit."
    
    reader = FileReader(PATH)

    assert reader.path    == PATH
    assert reader.content == CONTENT

    assert reader._FileReader__path    == PATH
    assert reader._FileReader__content == CONTENT
    
    assert isinstance(reader.path,    str)
    assert isinstance(reader.content, str)
def test_reader_immutable ():
    reader = FileReader(PATHS[0])

    check_immutable(reader, "path",    "new_path.txt")
    check_immutable(reader, "content", "Hello, World !")
    
def test_reader_alphabet ():
    reader = FileReader(PATHS[1])

    with reader as (atomic, state):
        for i in range(26):
            assert len(state) == 26 - i
            assert state.size == 26 - i
            assert chr(i + ord('a')) == state.peek()
            assert chr(i + ord('a')) == state.poll()
        assert state.size == 0

        with pytest.raises(Exception):
            state.peek()
        with pytest.raises(Exception):
            state.poll()
        assert state._FileReaderState__offset == 26
        assert state.size == 0
def test_reader_alphabet_rollback ():
    reader = FileReader(PATHS[1])

    with reader as (atomic, state):
        with reader as (atomic2, state2):
            for i in range(26):
                assert chr(i + ord('a')) == state2.poll()
            atomic2.rollback()
            
        for i in range(26):
            assert chr(i + ord('a')) == state.poll()
def test_reader_with_newlines ():
    reader = FileReader(PATHS[2])

    with open(PATHS[2], 'r') as file:
        text = file.read()
    
    offset = 0
    while offset != len(reader.content):
        read_size = random.randint(0, min(10, len(reader.content) - offset))
        with reader as (atomic, state):
            for i in range(read_size):
                assert state.peek() == reader.content[i + offset]
                assert state.poll() == reader.content[i + offset]

            if random.randint(0, 5) == 2:
                offset += read_size
            else:
                atomic.rollback()

def test_reader_with_newlines ():
    reader = FileReader(PATHS[2])

    content = reader.content

    for _iteration in range(100):
        with reader as (_atomic, _state):
    
            start = random.randint(0, len(content) - 1)
            end   = random.randint(0, len(content) - 1)
            end = start + 1

            if start > end: start, end = end, start

            cl = 1
            ln = 1

            with reader as (atomic, state):
                for i in range(start):
                    if state.poll() == '\n':
                        cl = 1
                        ln += 1
                    else: cl += 1
            sl, sn = cl, ln

            with reader as (atomic, state):
                for i in range(start, end):
                    if state.poll() == '\n':
                        cl = 1
                        ln += 1
                    else: cl += 1
                
                position = state.as_position()

                assert sl == position.column
                assert sn == position.line

                assert position.last_column == cl
                assert sn + position.height == ln + 1
            
            _atomic.rollback()