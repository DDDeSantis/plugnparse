import numpy as np
from typing import Union

epsilon = np.finfo(np.float64).eps
epsilon32 = np.finfo(np.float32).eps

ValidNumericTypes = (int, float, complex, np.number)
ValidRealNumericTypes = (int, float, np.number)

NumericType = Union[int, float, complex, np.number]
RealNumericType = Union[int, float, np.number]
