
class FileReader:
    __path    : str
    __content : str

    def __init__(self, path: str):
        self.__path = path

        with open(path, "r") as file:
            self.__content = file.read()

    @property
    def content (self):
        return self.__content
    @property
    def path (self):
        return self.__path