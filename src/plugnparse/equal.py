# --- external imports ---
from __future__ import annotations
from typing import Any, List, Tuple, Union
from .numerics import RealNumericType
import numpy as np


def equal(a: Any, b: Any, **kwargs) -> bool:
    """Checks if two objects are equal, using special logic depending on the type.

    Args:
        a: Any
        b: Any
            The two objects to compare.

    Keyword Args:
        rtol: float
            The relative tolerance for numeric values
        atol: float
            The absolute tolerance for numeric values

    Returns:
        bool:
            If the two objects are equal.
    """
    if isinstance(a, (int, float, np.number)):
        if not isinstance(b, (int, float, np.number)):
            return False
        return real_numerics_equal(a, b, **kwargs)
    elif type(a) != type(b):
        return False
    elif isinstance(a, (List, Tuple)):
        return iterables_equal(a, b, **kwargs)
    elif isinstance(a, (set, frozenset)):
        return sets_equal(a, b, **kwargs)
    elif isinstance(a, dict):
        return dicts_equal(a, b, **kwargs)
    elif isinstance(a, np.ndarray):
        return numpy_arrays_equal(a, b, **kwargs)
    elif hasattr(a, 'equals'):
        # Catches our Parsable class (and a few others)
        return a.equals(b, **kwargs)
    else:
        return a == b


def real_numerics_equal(a: RealNumericType, b: RealNumericType, **kwargs) -> bool:
    """Checks if two real numeric types are equal.

    Args:
        a: RealNumericType
        b: RealNumericType
            The two numbers to compare.

    Keyword Args:
        rtol: float
            The relative tolerance for numeric values
        atol: float
            The absolute tolerance for numeric values

    Returns:
        bool:
            If the two numbers are equal.
    """
    rtol = kwargs.get('rtol', None)
    atol = kwargs.get('atol', None)
    if rtol is None and atol is None:
        return a == b
    elif rtol is None:
        return np.allclose(a, b, atol=atol)
    elif atol is None:
        return np.allclose(a, b, rtol=rtol)

    return np.allclose(a, b, rtol=rtol, atol=atol)


def iterables_equal(a: Union[List, Tuple], b: Union[List, Tuple], **kwargs) -> bool:
    """Checks if two iterables are equal.

    Args:
        a: Union[List, Tuple]
        b: Union[List, Tuple]
            The two iterables to compare.

    Returns:
        bool:
            If the two iterables are equal.
    """
    if len(a) != len(b):
        return False

    for a_item, b_item in zip(a, b):
        if not equal(a_item, b_item, **kwargs):
            return False

    return True


def numpy_arrays_equal(a: np.ndarray, b: np.ndarray, **kwargs) -> bool:
    """Checks if two real numeric types are equal.

    Args:
        a: RealNumericType
        b: RealNumericType
            The two numbers to compare.

    Keyword Args:
        rtol: float
            The relative tolerance for numeric values
        atol: float
            The absolute tolerance for numeric values

    Returns:
        bool:
            If the two numbers are equal.
    """
    if a.dtype != b.dtype:
        return False

    if a.shape != b.shape:
        return False

    if issubclass(a.dtype.type, np.number):
        rtol = kwargs.get('rtol', None)
        atol = kwargs.get('atol', None)
        if rtol is None and atol is None:
            return np.array_equal(a, b, equal_nan=True)
        elif rtol is None:
            return np.allclose(a, b, atol=atol)
        elif atol is None:
            return np.allclose(a, b, rtol=rtol)

        return np.allclose(a, b, rtol=rtol, atol=atol)

    for a_item, b_item in zip(a.flatten(), b.flatten()):
        if not equal(a_item, b_item, **kwargs):
            return False

    return True


def sets_equal(a: Union[set, frozenset], b: Union[set, frozenset], **kwargs) -> bool:
    """Checks if two sets are equal.

    Args:
        a: Union[set, frozenset]
        b: Union[set, frozenset]
            The two sets to compare.

    Returns:
        bool:
            If the two sets are equal.
    """
    if len(a) != len(b):
        return False

    for a_item in a:
        found = False
        for b_item in b:
            if equal(a_item, b_item, **kwargs):
                found = True
                break

        if not found:
            return False

    return True


def dicts_equal(a: dict, b: dict, **kwargs) -> bool:
    """Checks if two dicts are equal.

    Args:
        a: dict
        b: dict
            The two dicts to compare.

    Returns:
        bool:
            If the two dicts are equal.
    """
    a_keys = set(a.keys())
    b_keys = set(b.keys())

    if not sets_equal(a_keys, b_keys, **kwargs):
        return False

    for key, a_item in a.items():
        if key not in b_keys:
            return False

        b_item = b[key]
        if not equal(a_item, b_item, **kwargs):
            return False

    return True
