
from typing import Any

import pytest

def check_immutable (object, varname: str, newvalue, exception=AttributeError):
    with pytest.raises(exception):
        setattr(object, varname, newvalue)
