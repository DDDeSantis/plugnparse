from __future__ import annotations

import pytest
import numpy as np

from plugnparse import equal, parsable


class TestParsable(parsable.Parsable):
    def __init__(self, value = None):
        super().__init__()
        self.value = value
        self._serializable_attributes.extend(['value'])

    @property
    def has_value(self):
        return self.value is not None

    def from_dict(self, input_value: dict):
        pass

    def to_dict(self) -> dict:
        pass

    def update(self, only_if_missing: bool, input_value: dict):
        pass


@pytest.mark.parametrize('a,b,kwargs,expected', [
    (1, "", {}, False),
    (1, 2, {}, False),
    (1, 1, {}, True),
    (1, 3, {'atol': 1}, False),
    (1, 2, {'atol': 1}, True),
    (3, 1, {'rtol': 1}, False),
    (1, 3, {'rtol': 1}, True),
    (0.1, 0.2, {}, False),
    (0.1, 0.1, {}, True),
    (0.1, 0.3, {'atol': 0.1}, False),
    (0.1, 0.2, {'atol': 0.1}, True),
    (0.3, 0.1, {'rtol': 1}, False),
    (0.1, 0.3, {'rtol': 1}, True),
    (np.int(1), np.int(2), {}, False),
    (np.int(1), np.int(1), {}, True),
    (np.int(1), np.int(3), {'atol': 1}, False),
    (np.int(1), np.int(2), {'atol': 1}, True),
    (np.int(3), np.int(1), {'rtol': 1}, False),
    (np.int(1), np.int(3), {'rtol': 1}, True),
    (np.float(0.1), np.float(0.2), {}, False),
    (np.float(0.1), np.float(0.1), {}, True),
    (np.float(0.1), np.float(0.3), {'atol': 0.1}, False),
    (np.float(0.1), np.float(0.2), {'atol': 0.1}, True),
    (np.float(0.3), np.float(0.1), {'rtol': 1}, False),
    (np.float(0.1), np.float(0.3), {'rtol': 1}, True),
    ((0, 1, 2), (1, 2, 3), {}, False),
    ((0, 1, 2), (0, 1, 2), {}, True),
    ((0, 1, 2), (2, 3, 4), {'atol': 1}, False),
    ((0, 1, 2), (1, 2, 3), {'atol': 1}, True),
    ((2, 3, 4), (0, 1, 2), {'rtol': 1}, False),
    ((0, 1, 2), (2, 3, 4), {'rtol': 1}, True),
    (("0", "1", "2"), (0, 1, 2), {}, False),
    (("0", "1", "2"), ("0", "1", "2"), {}, True),
    (("0", None, 2), ("0", "1", "2"), {}, False),
    (("0", None, 2), ("0", None, 2), {}, True),
    ([0, 1, 2], [1, 2, 3], {}, False),
    ([0, 1, 2], [0, 1, 2], {}, True),
    ([0, 1, 2], [2, 3, 4], {'atol': 1}, False),
    ([0, 1, 2], [1, 2, 3], {'atol': 1}, True),
    ([2, 3, 4], [0, 1, 2], {'rtol': 1}, False),
    ([0, 1, 2], [2, 3, 4], {'rtol': 1}, True),
    (["0", "1", "2"], [0, 1, 2], {}, False),
    (["0", "1", "2"], ["0", "1", "2"], {}, True),
    (["0", None, 2], ["0", "1", "2"], {}, False),
    (["0", None, 2], ["0", None, 2], {}, True),
    ({0, 1, 2}, {1, 2, 3}, {}, False),
    ({0, 1, 2}, {0, 1, 2}, {}, True),
    ({0, 1, 2}, {2, 1, 0}, {}, True),
    ({0, 1, 2}, {2, 3, 4}, {'atol': 1}, False),
    ({0, 1, 2}, {1, 2, 3}, {'atol': 1}, True),
    ({0, 1, 2}, {2.9, 1.9, 0.9}, {'atol': 1}, True),
    (frozenset((2, 3, 4)), frozenset((0, 1, 2)), {'rtol': 0}, False),
    (frozenset([0, 1, 2]), frozenset([2, 3, 4]), {'rtol': 1}, True)
])
def test_equal(a, b, kwargs, expected):
    actual = equal(a, b, **kwargs)
    assert actual == expected


@pytest.mark.parametrize('a,b,kwargs,expected', [
    (1, "", {}, False),
    (1, 2, {}, False),
    (1, 1, {}, True),
    (1, 3, {'atol': 1}, False),
    (1, 2, {'atol': 1}, True),
    (3, 1, {'rtol': 1}, False),
    (1, 3, {'rtol': 1}, True),
    (0.1, 0.2, {}, False),
    (0.1, 0.1, {}, True),
    (0.1, 0.3, {'atol': 0.1}, False),
    (0.1, 0.2, {'atol': 0.1}, True),
    (0.3, 0.1, {'rtol': 1}, False),
    (0.1, 0.3, {'rtol': 1}, True),
    (np.int(1), np.int(2), {}, False),
    (np.int(1), np.int(1), {}, True),
    (np.int(1), np.int(3), {'atol': 1}, False),
    (np.int(1), np.int(2), {'atol': 1}, True),
    (np.int(3), np.int(1), {'rtol': 1}, False),
    (np.int(1), np.int(3), {'rtol': 1}, True),
    (np.float(0.1), np.float(0.2), {}, False),
    (np.float(0.1), np.float(0.1), {}, True),
    (np.float(0.1), np.float(0.3), {'atol': 0.1}, False),
    (np.float(0.1), np.float(0.2), {'atol': 0.1}, True),
    (np.float(0.3), np.float(0.1), {'rtol': 1}, False),
    (np.float(0.1), np.float(0.3), {'rtol': 1}, True),
    ((0, 1, 2), (1, 2, 3), {}, False),
    ((0, 1, 2), (0, 1, 2), {}, True),
    ((0, 1, 2), (2, 3, 4), {'atol': 1}, False),
    ((0, 1, 2), (1, 2, 3), {'atol': 1}, True),
    ((2, 3, 4), (0, 1, 2), {'rtol': 1}, False),
    ((0, 1, 2), (2, 3, 4), {'rtol': 1}, True),
    (("0", "1", "2"), (0, 1, 2), {}, False),
    (("0", "1", "2"), ("0", "1", "2"), {}, True),
    (("0", None, 2), ("0", "1", "2"), {}, False),
    (("0", None, 2), ("0", None, 2), {}, True),
    ([0, 1, 2], [1, 2, 3], {}, False),
    ([0, 1, 2], [0, 1, 2], {}, True),
    ([0, 1, 2], [2, 3, 4], {'atol': 1}, False),
    ([0, 1, 2], [1, 2, 3], {'atol': 1}, True),
    ([2, 3, 4], [0, 1, 2], {'rtol': 1}, False),
    ([0, 1, 2], [2, 3, 4], {'rtol': 1}, True),
    (["0", "1", "2"], [0, 1, 2], {}, False),
    (["0", "1", "2"], ["0", "1", "2"], {}, True),
    (["0", None, 2], ["0", "1", "2"], {}, False),
    (["0", None, 2], ["0", None, 2], {}, True),
    ({0, 1, 2}, {1, 2, 3}, {}, False),
    ({0, 1, 2}, {0, 1, 2}, {}, True),
    ({0, 1, 2}, {2, 1, 0}, {}, True),
    ({0, 1, 2}, {2, 3, 4}, {'atol': 1}, False),
    ({0, 1, 2}, {1, 2, 3}, {'atol': 1}, True),
    ({0, 1, 2}, {2.9, 1.9, 0.9}, {'atol': 1}, True),
    (frozenset((2, 3, 4)), frozenset((0, 1, 2)), {'rtol': 0}, False),
    (frozenset([0, 1, 2]), frozenset([2, 3, 4]), {'rtol': 1}, True)
])
def test_parsable_equal(a, b, kwargs, expected):
    parsable_a = TestParsable(value=a)
    parsable_b = TestParsable(value=b)
    actual = equal(parsable_a, parsable_b, **kwargs)
    assert actual == expected
