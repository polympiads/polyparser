
from polyparser.io.reader import FileReader
from tests.utils.immutable import check_immutable

PATHS = [ "tests/io/file_tests/01.txt" ]

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
    