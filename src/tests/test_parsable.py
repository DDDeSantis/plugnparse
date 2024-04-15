# --- external imports ---
import pytest
from mock import patch, MagicMock
import numpy as np
# --- internal imports ---
from plugnparse import Parsable
from plugnparse import properties


class TestParsable:

    ##########################################################################
    # Test Simple Attributes
    ##########################################################################
    # --- test cases ---
    property_none_test_cases = list()
    # --- test case: name ---
    property_none_test_cases.append('version')

    @pytest.mark.parametrize("property_to_test", property_none_test_cases)
    def test_property_none(self, property_to_test):
        """Tests a property to properly handle None being set/get.

        Args:
            property_to_test: str
                A valid property of the class.
        """
        parameters = Parsable()
        setattr(parameters, property_to_test, None)
        assert not getattr(parameters, 'has_' + property_to_test)
        with pytest.raises(AttributeError):
            assert getattr(parameters, property_to_test)

    # --- test cases ---
    set_get_property_test_cases = list()
    # --- test case: name ---
    set_get_property_test_cases.append(('version', "foo", "foo", None, {}))
    set_get_property_test_cases.append(('version', 0.2, None, TypeError, {}))

    @pytest.mark.parametrize("property_to_test, value, expected, error, kwargs", set_get_property_test_cases)
    def test_property_set_get(self, property_to_test, value, expected, error, kwargs):
        """Tests a property to properly handle a raw value being set/get.

        Args:
            property_to_test: str
                A valid property of the class.
            value:
                The value to set to the property.
            expected:
                The expected value returned from the getter.
            error:
                The error that is raised, if any.
        """
        class_obj = Parsable(**kwargs)
        if error is None:
            setattr(class_obj, property_to_test, value)
            assert getattr(class_obj, 'has_' + property_to_test)
            assert getattr(class_obj, property_to_test) == expected
        else:
            with pytest.raises(error):
                setattr(class_obj, property_to_test, value)
                getattr(class_obj, property_to_test)

    ##########################################################################
    # Test Decorators
    ##########################################################################
    def test_static_class_setter(self):
        """Tests a static class setter on an arbitrary Parsable class."""
        class TestClass(Parsable):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._serializable_attributes.extend(['foo'])
                self.foo = kwargs.get('foo')

            @property
            def has_foo(self):
                return self._foo is not None

            @property
            def foo(self):
                if self._foo is None:
                    raise AttributeError("No foo")
                return self._foo

            @foo.setter
            def foo(self, value):
                self._foo = value

        class TargetClass:

            def __init__(self, *args, **kwargs):

                self.test_class = kwargs.get('test_class')

            @property
            def test_class(self):
                if self._test_class is None:
                    raise AttributeError("No test_class")
                return self._test_class

            @test_class.setter
            @TestClass.static_class_setter()
            def test_class(self, value):
                self._test_class = value

        # --- create a test class json dictionary ---
        test_class_json = {properties.generic_parsable_type: TestClass.__name__,
                           properties.generic_parsable_module: TestClass.__module__,
                           'foo': 1}

        # --- create the target class ---
        target_class = TargetClass(test_class=test_class_json)

        # --- assert all the attributes were successfully parsed ---
        assert isinstance(target_class.test_class,  TestClass)
        assert target_class.test_class.foo == 1

    ##########################################################################
    # Test Parsing Order
    ##########################################################################

    def test_collect_all_attributes(self):

        parsable_class = Parsable()
        parsable_class._serializable_attributes.append('foo')
        parsable_class._enum_attributes.append('bar')
        parsable_class._parsable_attributes.append('baz')
        parsable_class._specialized_attributes.append('foo-bar')
        parsable_class._dict_of_parsables.append('foo-baz')
        parsable_class._list_of_parsables.append('foo-foo')

        assert parsable_class.collect_all_attributes() == ['version', 'foo', 'bar', 'baz', 'foo-bar', 'foo-baz', 'foo-foo']

    # --- test cases ---
    test_split_ordered_test_casts = list()
    # --- test case: positive ---
    test_split_ordered_test_casts.append((['foo', 'bar', 'baz'], ['bing', 'bang', 'foo', 'baz', 'ring', 'bar'],
                                          ['foo', 'bar', 'baz'], ['bing', 'bang', 'ring'], None))
    test_split_ordered_test_casts.append(([], ['bing, bang', 'foo', 'baz', 'ring', 'bar'],
                                          [], ['bing, bang', 'foo', 'baz', 'ring', 'bar'], None))
    # --- test case: negative ---
    test_split_ordered_test_casts.append((['foo', 'boom', 'baz'], ['bing, bang', 'foo', 'baz', 'ring', 'bar'],
                                          ['foo', 'bar', 'baz'], ['bing', 'bang', 'ring'], ValueError))

    @pytest.mark.parametrize("ordered_list, collected_attributes, expected_ordered, expected_unordered, error", test_split_ordered_test_casts)
    def test_split_ordered_and_unordered_attributes(self, ordered_list, collected_attributes, expected_ordered, expected_unordered, error):

        parsable_class = Parsable()
        parsable_class._desired_order_of_parsing = ordered_list
        with patch.object(Parsable, 'collect_all_attributes', return_value=collected_attributes):
            if error is None:
                ordered_output, unordered_output = parsable_class.split_ordered_and_unordered_attributes()
                assert ordered_output == expected_ordered
                assert unordered_output == expected_unordered
            else:
                with pytest.raises(error):
                    ordered_output, unordered_output = parsable_class.split_ordered_and_unordered_attributes()
