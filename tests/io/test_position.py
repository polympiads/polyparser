
from polyparser.io.position import Position
from polyparser.io.reader import FileReader
from tests.utils.immutable import check_immutable
from tests.utils.typechecking import check_type_checking

def test_position_type_checking ():
    check_type_checking("polyparser.io.position")

def test_simple_position ():
    reader = FileReader("tests/io/file_tests/01.txt")

    pos = Position(reader, 0, 0, 1, 10)

    assert pos.line   == 0
    assert pos.column == 0
    assert pos.width  == 10
    assert pos.height == 1

    check_immutable( pos, "line",   11 )
    check_immutable( pos, "column", 11 )
    check_immutable( pos, "width",  11 )
    check_immutable( pos, "height", 11 )