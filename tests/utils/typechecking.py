
import importlib
import sys

from typing import *

TYPE_CHECKING = True

def check_type_checking (module: str):
    typing_module = sys.modules["typing"]

    sys.modules["typing"] = sys.modules["tests.utils.typechecking"]

    _module_copy = {}
    for key in list( sys.modules.keys() ):
        if key.startswith("polyparser.") or key == "polyparser":
            _module_copy[key] = sys.modules[key]
        
            del sys.modules[key]

    new_module = importlib.import_module(module)

    for key in list( sys.modules.keys() ):
        if key.startswith("polyparser.") or key == "polyparser":
            del sys.modules[key]
    
    for key in _module_copy.keys():
        sys.modules[key] = _module_copy[key]
    sys.modules["typing"] = typing_module
