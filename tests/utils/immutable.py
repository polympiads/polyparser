
from typing import Any

import pytest

def check_immutable (object, varname: str, newvalue):
    with pytest.raises(AttributeError):
        setattr(object, varname, newvalue)
