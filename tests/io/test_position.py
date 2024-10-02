
from polyparser.io.position import PositionRange
from polyparser.io.reader import FileReader
from tests.utils.immutable import check_immutable

def test_simple_position ():
    reader = FileReader("tests/io/file_tests/01.txt")

    pos = PositionRange(reader, 0, 0, 1, 10)

    assert pos.line   == 0
    assert pos.column == 0
    assert pos.last_column == 10
    assert pos.height == 1

    check_immutable( pos, "line",   11 )
    check_immutable( pos, "column", 11 )
    check_immutable( pos, "last_column",  11 )
    check_immutable( pos, "height", 11 )