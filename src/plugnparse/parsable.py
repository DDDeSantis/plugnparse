# --- external imports ---
from __future__ import annotations
from typing import List, Optional, Tuple, Union, Any, Sequence, Callable, TypeVar
import numpy as np
from pathlib import Path
# --- local imports ---
from . import logger, io, properties
from .equal import equal

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")

class Parsable:
    """Represents a class capable of parsing attributes of its subclass implementations.

    Notes:
        The Parsable class automatically parses properties of its subclasses which follow a dedicated pattern.
        Given a subclass has registered a property named 'foo' to be parsed then the subclass must have the following
        three implementations given that 'foo' can be set, retrieved, and is able to not have a value:

        ---

        @property
        def has_foo(self) -> bool: ...

        @property
        def foo(self) -> T: ...

        @foo.setter
        def foo(self, input_value): ...

        ---

        If the 'foo' is not settable then the setter may be omitted. If 'foo' is guaranteed to always contain a valid
        value then 'has_foo' can be omitted.

        If a certain update routine is desired for a particular property then an additional method can be defined as
        such:

        ---

        def update_foo(self, input_value): ...

        ---

        When defined, 'update_foo', will be used in place of the 'foo' setter when 'update()' is called on this class.

        In addition, each attribute must fall into one of the predefined categories of parsing types. The categories are
        as follows:

        - Serializable:
            Attributes that are primitive type such as numbers, strings, list of string or numbers, dictionary of
            strings or numbers, or entities that have a method 'tolist()' that converts its contents to a list of
            numbers or strings such as numpy arrays. All of these types are basic types that the JSON encoder handles
            by default. To register a property as serializable, the subclass must append the property name onto
            the end of the list '_serializable_attributes'.
        - Enum:
            Attributes that are simple enums, not list of enums or dict of enums. This parsing routine converts the
            enums to and from strings using their name property. To register a property for enum parsing, the subclass
            must append the property name onto the end of the list '_enum_attributes'. In the subclass implementation
            the property setter functions should provide the @enum_setter() decorator for efficient deserialization.
        - Parsable:
            Attributes that are objects whose type is derived from the base class Parsable. This allows those
            attributes to have a contained parsing routine which outputs a dictionary which maps their internal
            attribute names to their values. This can create a chain of hierarchical parsing of classes. To register a
            property as a 'Parsable', the subclass must append the property name onto the end of the list
            '_parsable_attributes'. In the subclass implementation the property setter functions should provide the
            @parsable_setter() decorator for efficient deserialization.
        - Dictionary of Parsables:
            Attributes which contain a dictionary mapping of serializable keys to parsable objects as their values.
            To register a property for as a dictionary of parsables, the subclass must append the property name onto
             the end of the list '_dict_of_parsables'.
        - List of Parsables:
            Attributes which contain an ordered list of parsable objects. To register a property for as a list of
            parsables, the subclass must append the property name onto the end of the list '_list_of_parsables'.
        - Specialized:
            All other types of attributes that require specialized encoding and decoding functions. For these
            attributes they much have implementations of functions named 'foo_encode()' and 'foo_decode(input)' for
            the attribute named 'foo'. The function 'foo_encode()' would return the serializable representation of 'foo'
            while 'foo_decode(input)' would take the serialized 'input' and set its deserialized representation to
            'foo'. To register a property for specialized parsing, the subclass must append the property name onto the
            end of the list '_specialized_attributes'.

        The proper way of registering properties of a subclass of Parsable is demonstrated next:

        ---

        class FooClass(Parsable)

            def __init__(self, *args, **kwargs):
                # --- init the parent ---
                super().__init__(*args, **kwargs)
                # --- set up the parsable attributes ---
                self._serializable_attributes.extend(['foo'])
                self._specialized_attributes.extend(['bar'])

                # --- set components ---
                self.foo = kwargs.get('foo')
                self.bar = kwargs.get('bar')

            @property
            def has_foo(self) -> bool:
                return self._foo is not None

            @property
            def foo(self) -> int:
                if self._foo is None:
                    logger.log_and_raise(AttributeError, "The foo has not been set.", record_location=True)
                return self._foo

            @foo.setter
            def foo(self, input_value):
                if input_value is None or (isinstance(input_value, int) and input_value >= 0):
                    self._foo = input_value
                else:
                    logger.log_and_raise(TypeError, "Invalid type [", type(input_value), "].", record_location=True)

            @property
            def has_bar(self) -> bool:
                return self._bar is not None

            @property
            def bar(self) -> Bar:
                if self._bar is None:
                    logger.log_and_raise(AttributeError, "The bar has not been set.", record_location=True)
                return self._bar

            @bar.setter
            def bar(self, input_value):
                if input_value is None or isinstance(input_value, Bar):
                    self._bar = input_value
                else:
                    logger.log_and_raise(TypeError, "Invalid type [", type(input_value), "].", record_location=True)

            def bar_encode(self):
                return str(self.bar)

            def bar_decode(self, input_value):
                self.bar = Bar.from_str(input_value)

        ---

        Finally, some subclasses may require that attributes are parsed in a specific order. To enable this feature,
        simply append the attributes that are to be parsed first to the list '_desired_order_of_parsing' in the order
        that the attributes should be parsed. Attributes that do not require a specific order of parsing can be omitted
        from this list. They will be parsed, in no specific order, after all registered attributes in
        '_desired_order_of_parsing' have been parsed. The attributes registered in '_desired_order_of_parsing' must be
        also be registered in one of the above category lists. Registering an attribute that is not also registered in
        a category will cause the parsing routine to raise an exception.
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        # --- categories of parsable attributes ---
        self._serializable_attributes = []
        self._enum_attributes = []
        self._parsable_attributes = []
        self._specialized_attributes = []
        self._dict_of_parsables = []
        self._list_of_parsables = []

        # --- order of parsing ---
        self._desired_order_of_parsing = []

        # --- update the parsable attributes ---
        self._serializable_attributes.extend(['version'])

        # --- version ---
        self.version = kwargs.get('version')

    ##########################################################################
    # Version Properties
    ##########################################################################
    @property
    def has_version(self) -> bool:
        """Returns whether the version attribute has been assigned."""
        return self._version is not None

    @property
    def version(self) -> str:
        """Gets the specific version of this implementation of the Parsable class.

        Notes:
            The version should be incremented for every interface change made to a concrete implementation of the
            Parsable class. This is meant to assist in the migration of evolving parameters in datasets.

        Returns:
            str:
                A string representation of the version.

        Raises:
            AttributeError:
                If the property has not been assigned yet.
        """
        if self._version is None:
            logger.log_and_raise(AttributeError, "The version parameter has not been set.")
        return self._version

    @version.setter
    def version(self, input_value: Optional[str]):
        """Sets the specific version of this implementation of the Parsable class.

        Args:
            input_value: Optional[str]
                Either None or a string representation of the version of this parameter implementation.

        Raises:
            TypeError:
                If the provided `input_value` is not a supported type.
        """
        if input_value is None or isinstance(input_value, str):
            self._version = input_value
        else:
            logger.log_and_raise(TypeError, "Invalid input type [", type(input_value), "].")

    ##########################################################################
    # Decorators
    ##########################################################################
    @classmethod
    def static_class_setter(cls) -> Callable[[Callable[[T,U],V]],Callable[[T,Union[U,dict]],V]]:
        """A decorator function that provides the class module and name to the module loader routine.

        Examples:
            from plugnparse.parsable import Parsable

            class Foo(Parsable):
                def to_dict(self) -> dict:
                    return {}

                def from_dict(self, input_value: dict):
                    if 'foo' in input_value:
                        print("The foo is ", input_value['foo'])

                def update(self, only_if_missing: bool, input_value: dict):
                    pass

            class Bar:
                @property
                def bar(self):
                    return 'bar'

                @bar.setter
                @Foo.static_class_setter()
                def bar(self, input_value):
                    if not isinstance(input_value, Foo):
                        raise ValueError("Not a Foo!")

            bar = Bar()
            bar.bar = {'foo': 'baz'}

            Output:
            'The foo is baz'

        Returns:
            A python functor that can be place as a decorator for automatically parsing 'cls' without needing
            to provide the module or class name in the parsable dictionary.
        """
        return properties.parsable_setter(class_type=cls)

    ##########################################################################
    # Parsing Order
    ##########################################################################
    def collect_all_attributes(self) -> List[str]:
        """Returns a collective list of all registered attributes in no particular order."""
        output = list()
        output.extend(self._serializable_attributes)
        output.extend(self._enum_attributes)
        output.extend(self._parsable_attributes)
        output.extend(self._specialized_attributes)
        output.extend(self._dict_of_parsables)
        output.extend(self._list_of_parsables)
        return output

    def split_ordered_and_unordered_attributes(self) -> Tuple[List[str], List[str]]:
        """Splits the attributes between those that are to be parsed in a certain order and the rest of the attributes.

        Returns:
            Tuple[List[str], List[str]]:
                The ordered and unordered attributes respectively.

        Raises:
            ValueError:
                If there are attributes registered in the '_desired_order_of_parsing' property that are not
                registered in any of the attributes categories.
        """
        # --- collect the attributes ---
        ordered_attributes = np.asanyarray(self._desired_order_of_parsing)
        all_attributes = np.asanyarray(self.collect_all_attributes())

        # --- trivial case ---
        if ordered_attributes.size == 0:
            return [], all_attributes.tolist()

        # --- ensure that all ordered attributes exist in the list of attributes ---
        exist = np.in1d(ordered_attributes, all_attributes)
        if not np.all(exist):
            missing_attributes = ordered_attributes[np.argwhere(np.logical_not(exist))]
            logger.log_and_raise(ValueError, "The desired ordered attributes [", missing_attributes,
                                 "] are missing from the registered attributes for class [",
                                 self.__class__.__name__, "].")

        # --- get the attributes that are not in the list of ordered attributes ---
        unordered_attributes = all_attributes[np.argwhere(np.logical_not(np.in1d(all_attributes, ordered_attributes)))]
        unordered_attributes = unordered_attributes.ravel()
        # --- return the ordered attributes and the unordered attributes ---
        return ordered_attributes.tolist(), unordered_attributes.tolist()

    ##########################################################################
    # Conversions
    ##########################################################################
    @staticmethod
    def serialized_dict(input_value: dict) -> dict:
        """Converts a dictionary of serializable and parsable values into their serialized representation.

        Args:
            input_value: dict
                A dictionary of serializable keys mapping to objects that contain either a 'to_dict()' or 'tolist()'
                method. Values which do not contain one of these two methods are placed into the output dictionary
                as is. The exception being if there is a list of objects for the value of a key-value pair, i.e.
                input_value={'key1': [object1, object2], 'key2': [object3, object4]}. In this case the objects
                are expected to have one of the two methods mentioned above.

        Returns:
            dict
                The serialized representation of the 'input_value'.
        """
        parsed_items = dict()
        for key, value in input_value.items():
            if hasattr(value, 'to_dict'):
                parsed_items[key] = value.to_dict()
            elif hasattr(value, 'tolist'):
                parsed_items[key] = value.tolist()
            elif isinstance(value, list):
                converted_items = []
                for item in value:
                    if hasattr(value, 'to_dict'):
                        converted_items.append(item.to_dict())
                    elif hasattr(value, 'tolist'):
                        converted_items.append(item.tolist())
                    else:
                        converted_items.append(item)
                parsed_items[key] = converted_items
            else:
                parsed_items[key] = value
        return parsed_items

    @staticmethod
    def serialized_list(input_value: list) -> list:
        """Converts a list of serializable and parsable values into their serialized representation.

        Args:
            input_value: list
                A list of objects that contain either a 'to_dict()' or 'tolist()' method. Objects which do not contain
                one of these two methods are placed into the output list as is. The exception being if there is a single
                nesting of a list, i.e. input_value=[[object1, object2], [object3, object4]]. In this case the objects
                are expected to have one of the two methods mentioned above.
        Returns:
            list:
                The serialized representation of the 'input_value'.
        """
        parsed_items = list()
        for item in input_value:
            if hasattr(item, 'to_dict'):
                parsed_items.append(item.to_dict())
            elif hasattr(item, 'tolist'):
                parsed_items.append(item.tolist())
            elif isinstance(item, list):
                for entry in item:
                    if hasattr(entry, 'to_dict'):
                        parsed_items.append(entry.to_dict())
                    elif hasattr(entry, 'tolist'):
                        parsed_items.append(entry.tolist())
                    else:
                        parsed_items.append(entry)
            else:
                parsed_items.append(item)
        return parsed_items

    @staticmethod
    def parsed_dict(input_value: dict) -> dict:
        """Converts a dictionary of serializable and parsable values from their serialized representation.

        Args:
            input_value: dict
                A dictionary of serialized keys mapping to the serialized dictionary representation of Parsable
                subclasses. Vales that are not dictionaries or do not contain the key defined at
                'plugnparse.properties.generic_parsable_type' are placed into the output dictionary as is.

        Returns:
            dict:
                The deserialized representation of the 'input_value'.
        """
        parsed_items = dict()
        for key, value in input_value.items():
            if isinstance(value, dict):
                if properties.generic_parsable_type in value:
                    parsed_items[key] = properties.parse(value, throw_if_unable_to_parse=True)
                else:
                    parsed_items[key] = value
            elif isinstance(value, list):
                converted_items = []
                for item in value:
                    if isinstance(item, dict):
                        if properties.generic_parsable_type in item:
                            converted_items.append(properties.parse(item, throw_if_unable_to_parse=True))
                        else:
                            converted_items.append(item)
                    else:
                        converted_items.append(item)
                parsed_items[key] = converted_items
            else:
                parsed_items[key] = value
        return parsed_items

    @staticmethod
    def parsed_list(input_value: list) -> list:
        """Converts a list of serializable and parsable values from their serialized representation.

        Args:
            input_value: list
                A list of serialized dictionary representation of Parsable subclasses. Objects that are not dictionaries
                or do not contain the key defined at 'plugnparse.properties.generic_parsable_type' are placed into
                the output list as is.

        Returns:
            list
                The deserialized representation of the 'input_value'.
        """
        parsed_items = list()
        for item in input_value:
            if isinstance(item, dict):
                if properties.generic_parsable_type in item:
                    parsed_items.append(properties.parse(item, throw_if_unable_to_parse=True))
                else:
                    parsed_items.append(item)
            elif isinstance(item, list):
                converted_items = []
                for entry in item:
                    if isinstance(entry, dict):
                        if properties.generic_parsable_type in entry:
                            converted_items.append(properties.parse(entry, throw_if_unable_to_parse=True))
                        else:
                            converted_items.append(entry)
                    else:
                        converted_items.append(entry)
                parsed_items.append(converted_items)
            else:
                parsed_items.append(item)
        return parsed_items

    ##########################################################################
    # Serialize/Deserialize To/From a String
    ##########################################################################
    def to_string(self, **kwargs) -> str:
        """Converts a Parsable subclass to a JSON string.

        Args:
            **kwargs:
                Optional keyword arguments to pass to the Parsable subclass.

        Returns:
            str:
                The JSON representation of the Parsable subclass.
        """
        return io.to_json_string(self.to_dict(), **kwargs)

    def from_string(self, json_string: str):
        """Parses a JSON string into the Parsable subclass.

        Args:
            json_string: str
                The JSON representation of the Parsable subclass.
        """
        self.from_dict(io.from_json_string(json_string))

    ##########################################################################
    # Serialize To a Dictionary
    ##########################################################################
    def to_dict(self) -> dict:
        """Serializes the internal attributes into JSON compatible dictionary.

        Returns:
            dict:
                The dictionary holding serializable keys mapping to the serialized representations of the values of
                internal attributes.
        """
        output = dict()
        output[properties.generic_parsable_type] = self.__class__.__name__
        output[properties.generic_parsable_module] = self.__class__.__module__

        # --- serializable ---
        for property_name in self._serializable_attributes:
            self.to_dict_serializable(output, property_name)

        # --- enums ---
        for property_name in self._enum_attributes:
            self.to_dict_enum(output, property_name)

        # --- parsable ---
        for property_name in self._parsable_attributes:
            self.to_dict_parsable(output, property_name)

        # --- dict of parsables ---
        for property_name in self._dict_of_parsables:
            self.to_dict_dict_of_parsable(output, property_name)

        # --- list of parsables ---
        for property_name in self._list_of_parsables:
            self.to_dict_list_of_parsable(output, property_name)

        # --- specialized ---
        for property_name in self._specialized_attributes:
            self.to_dict_specialized(output, property_name)
        return output

    def to_dict_serializable(self, output: dict, property_name: str):
        """Retrieves the serializable attribute and populates the output dictionary with its serialized representation.

        Args:
            output: dict
                The output dictionary of serialized attributes for which to modify inplace.
            property_name: str
                The name of the serializable attribute to retrieve from this Parsable subclass.
        """
        if hasattr(self, "has_" + property_name):
            if self.__getattribute__("has_" + property_name):
                value = self.__getattribute__(property_name)
                if hasattr(value, 'tolist'):
                    value = value.tolist()
                if isinstance(value, frozenset):
                    value = list(value)
                output[property_name] = value
        else:
            value = self.__getattribute__(property_name)
            if hasattr(value, 'tolist'):
                value = value.tolist()
            if isinstance(value, frozenset):
                value = list(value)
            output[property_name] = value

    def to_dict_enum(self, output: dict, property_name: str):
        """Retrieves the enum attribute and populates the output dictionary with its serialized representation.

        Args:
            output: dict
                The output dictionary of serialized attributes for which to modify inplace.
            property_name: str
                The name of the enum attribute to retrieve from this Parsable subclass.
        """
        if hasattr(self, "has_" + property_name):
            if self.__getattribute__("has_" + property_name):
                output[property_name] = self.__getattribute__(property_name).name
        else:
            output[property_name] = self.__getattribute__(property_name).name

    def to_dict_parsable(self, output: dict, property_name: str):
        """Retrieves the Parsable attribute and populates the output dictionary with its serialized representation.

        Args:
            output: dict
                The output dictionary of serialized attributes for which to modify inplace.
            property_name: str
                The name of the Parsable attribute to retrieve from this Parsable subclass.
        """
        if hasattr(self, "has_" + property_name):
            if self.__getattribute__("has_" + property_name):
                output[property_name] = self.__getattribute__(property_name).to_dict()
        else:
            output[property_name] = self.__getattribute__(property_name).to_dict()

    def to_dict_dict_of_parsable(self, output: dict, property_name: str):
        """
        Retrieves the attribute whose value is a dictionary of Parsable objects and populates the output dictionary
        with its serialized representation.

        Args:
            output: dict
                The output dictionary of serialized attributes for which to modify inplace.
            property_name: str
                The name of the attribute whose value is a dictionary of Parsable objects to retrieve from this
                Parsable subclass.
        """
        if hasattr(self, "has_" + property_name):
            if self.__getattribute__("has_" + property_name):
                item = self.__getattribute__(property_name)
                if isinstance(item, dict):
                    output[property_name] = Parsable.serialized_dict(item)
        else:
            item = self.__getattribute__(property_name)
            if isinstance(item, dict):
                output[property_name] = Parsable.serialized_dict(item)

    def to_dict_list_of_parsable(self, output: dict, property_name: str):
        """
        Retrieves the attribute whose value is a list of Parsable objects and populates the output dictionary
        with its serialized representation.

        Args:
            output: dict
                The output dictionary of serialized attributes for which to modify inplace.
            property_name: str
                The name of the attribute whose value is a list of Parsable objects to retrieve from this
                Parsable subclass.
        """
        if hasattr(self, "has_" + property_name):
            if self.__getattribute__("has_" + property_name):
                item = self.__getattribute__(property_name)
                if isinstance(item, (Sequence, set, frozenset)):
                    output[property_name] = Parsable.serialized_list(list(item))

        else:
            item = self.__getattribute__(property_name)
            if isinstance(item, (Sequence, set, frozenset)):
                output[property_name] = Parsable.serialized_list(list(item))

    def to_dict_specialized(self, output: dict, property_name: str):
        """
        Retrieves the attribute whose value is requires a specialized encoding function and populates the output
        dictionary with its serialized representation.

        Args:
            output: dict
                The output dictionary of serialized attributes for which to modify inplace.
            property_name: str
                The name of the attribute to retrieve from this Parsable subclass. This subclass must have
                a method named ''property_name'_encode'. For example for a property_name = 'foo', a method should exist
                named 'foo_encode'.

        Raises:
            AttributeError: If the Parsable subclass does not have a method named ''property_name'_encode'.
        """
        if hasattr(self, property_name + '_encode'):
            if hasattr(self, "has_" + property_name):
                if self.__getattribute__("has_" + property_name):
                    output[property_name] = self.__getattribute__(property_name + '_encode')()
            else:
                output[property_name] = self.__getattribute__(property_name + '_encode')()
        else:
            logger.log_and_raise(AttributeError, "Unable to construct attribute [", property_name,
                                 "] since there is no function [", property_name + '_encode', "].")

    ##########################################################################
    # Deserialize From a Dictionary
    ##########################################################################
    def from_dict(self, input_value: dict):
        """Populates the internal attributes from the dictionary of the serialized representation of their values.

        Args:
            input_value: dict
                The serialized dictionary that is to be deserialized and used to hydrate the internal structures of this
                subclass implementation.
        """
        ordered_attributes, unordered_attributes = self.split_ordered_and_unordered_attributes()
        for property_name in (*ordered_attributes, *unordered_attributes):
            if property_name in self._serializable_attributes:
                self.from_dict_serializable(input_value, property_name)
            elif property_name in self._parsable_attributes:
                self.from_dict_parsable(input_value, property_name)
            elif property_name in self._enum_attributes:
                self.from_dict_enum(input_value, property_name)
            elif property_name in self._dict_of_parsables:
                self.from_dict_dict_of_parsable(input_value, property_name)
            elif property_name in self._list_of_parsables:
                self.from_dict_list_of_parsable(input_value, property_name)
            elif property_name in self._specialized_attributes:
                self.from_dict_specialized(input_value, property_name)
            else:
                logger.log_and_raise(RuntimeError, "The property [", property_name, "] doesn't exist!")

    def from_dict_serializable(self, input_value: dict, property_name: str):
        """Retrieves the serializable value from the input dictionary and populates the desired attribute.

        Args:
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the serializable attribute to populate. This attribute is only populated if the
                'property_name' is settable and is in the 'input_value'.
        """
        if property_name in input_value:
            if properties.can_set(self, property_name):
                self.__setattr__(property_name, input_value.get(property_name))

    def from_dict_enum(self, input_value: dict, property_name: str):
        """Retrieves the enum value from the input dictionary and populates the desired attribute.

        Args:
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the enum attribute to populate. This attribute is only populated if the
                'property_name' is settable and is in the 'input_value'. Attributes must have an @enum_setter()
                decorator on the property setter functions.
        """
        self.from_dict_serializable(input_value, property_name)

    def from_dict_parsable(self, input_value: dict, property_name: str):
        """Retrieves the Parsable value from the input dictionary and populates the desired attribute.

        Args:
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the Parsable attribute to populate. This attribute is only populated if the
                'property_name' is settable and is in the 'input_value'. Attributes must have a @parsable_setter()
                decorator on the property setter functions or be able to parse the input value within the setter.
        """
        self.from_dict_serializable(input_value, property_name)

    def from_dict_dict_of_parsable(self, input_value: dict, property_name: str):
        """
        Retrieves the attribute whose value is a dictionary of Parsable objects from the input dictionary and
        populates the desired attribute.

        Args:
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute whose value is a dictionary of Parsable objects to populate. This
                attribute is only populated if the 'property_name' is settable and is in the 'input_value'.
        """
        if property_name in input_value:
            if properties.can_set(self, property_name):
                value = input_value.get(property_name)
                if isinstance(value, dict):
                    value = Parsable.parsed_dict(value)
                self.__setattr__(property_name, value)

    def from_dict_list_of_parsable(self, input_value: dict, property_name: str):
        """
        Retrieves the attribute whose value is a list of Parsable objects from the input dictionary and
        populates the desired attribute.

        Args:
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute whose value is a list of Parsable objects to populate. This
                attribute is only populated if the 'property_name' is settable and is in the 'input_value'.
        """
        if property_name in input_value:
            if properties.can_set(self, property_name):
                value = input_value.get(property_name)
                if isinstance(value, list):
                    value = Parsable.parsed_list(value)
                self.__setattr__(property_name, value)

    def from_dict_specialized(self, input_value: dict, property_name: str):
        """
        Retrieves the attribute whose value is requires a specialized decoding function from the input dictionary
        and populates the desired attribute.

        Args:
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute to populate. This attribute is only populated if the 'property_name' is
                settable and is in the 'input_value'. This subclass must have a method named ''property_name'_decode'.
                For example for a property_name = 'foo', a method should exist named 'foo_decode'.

        Raises:
            AttributeError: If the Parsable subclass does not have a method named ''property_name'_decode'.
        """
        if property_name in input_value:
            if hasattr(self, property_name + '_decode'):
                self.__getattribute__(property_name + '_decode')(input_value.get(property_name))
            else:
                logger.log_and_raise(AttributeError, "Unable to decode attribute [", property_name,
                                     "] since there is no function [", property_name + '_decode', "].")

    ##########################################################################
    # Update Via Deserializing From a Dictionary
    ##########################################################################
    def update(self, only_if_missing: bool, input_value: dict):
        """Updates the internal attributes from the dictionary of the serialized representation of their values.

        Notes:
            This function differs from 'from_dict()' in that it allows for selective updating of the values depending
            on whether the attributes are already populated.

        Args:
            only_if_missing: bool
                If True then attributes whose values are not currently populated will be updated. If False, then
                the attributes will be updated regardless of their current status.
            input_value: dict
                The serialized dictionary that is to be deserialized and used to hydrate the internal structures of this
                subclass implementation.
        """
        ordered_attributes, unordered_attributes = self.split_ordered_and_unordered_attributes()

        for property_name in (*ordered_attributes, *unordered_attributes):
            if property_name in self._serializable_attributes:
                self.update_serializable_property(only_if_missing, input_value, property_name)
            elif property_name in self._parsable_attributes:
                self.update_parsable_property(only_if_missing, input_value, property_name)
            elif property_name in self._enum_attributes:
                self.update_enum_property(only_if_missing, input_value, property_name)
            elif property_name in self._dict_of_parsables:
                self.update_dict_of_parsable_property(only_if_missing, input_value, property_name)
            elif property_name in self._list_of_parsables:
                self.update_list_of_parsable_property(only_if_missing, input_value, property_name)
            elif property_name in self._specialized_attributes:
                self.update_specialized_property(only_if_missing, input_value, property_name)
            else:
                logger.log_and_raise(RuntimeError, "The property [", property_name, "] doesn't exist!")

    def update_property(self, input_value: Any, property_name: str):
        """Updates a property of this class.

        Args:
            input_value: Any
                A value of any kind with which the property will be updated.
            property_name: str
                The name of the attribute to populate.
        """
        if hasattr(self, name := "update_" + property_name) and callable(updater := getattr(self, name)):
            updater(input_value)
        elif properties.can_set(self, property_name):
            self.__setattr__(property_name, input_value)
        else:
            logger.debug("Unable to update property [", property_name, "].", record_location=True)

    def update_serializable_property(self, only_if_missing: bool, input_value: dict, property_name: str):
        """Retrieves the serializable value from the input dictionary and populates the desired attribute if desired.

        Args:
            only_if_missing: bool
                Indicates whether the attribute should be updated only if it does not currently have a value assigned.
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute to populate.
        """
        if only_if_missing:
            if hasattr(self, "has_" + property_name):
                if self.__getattribute__("has_" + property_name):
                    return
        if property_name in input_value:
            self.update_property(input_value.get(property_name), property_name)

    def update_enum_property(self, only_if_missing: bool, input_value: dict, property_name: str):
        """Retrieves the enum value from the input dictionary and populates the desired attribute if desired.

        Args:
            only_if_missing: bool
                Indicates whether the attribute should be updated only if it does not currently have a value assigned.
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute to populate.
        """
        self.update_serializable_property(only_if_missing, input_value, property_name)

    def update_parsable_property(self, only_if_missing: bool, input_value: dict, property_name: str):
        """Retrieves the Parsable value from the input dictionary and populates the desired attribute if desired.

        Args:
            only_if_missing: bool
                Indicates whether the attribute should be updated only if it does not currently have a value assigned.
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute to populate.
        """
        self.update_serializable_property(only_if_missing, input_value, property_name)

    def update_dict_of_parsable_property(self, only_if_missing: bool, input_value: dict, property_name: str):
        """Retrieves the attribute whose value is a dictionary of Parsable objects from the input dictionary and
        populates the desired attribute if desired.

        Args:
            only_if_missing: bool
                Indicates whether the attribute should be updated only if it does not currently have a value assigned.
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute to populate.
        """
        if only_if_missing:
            if hasattr(self, "has_" + property_name):
                if self.__getattribute__("has_" + property_name):
                    return
        if property_name in input_value:
            value = input_value.get(property_name)
            if isinstance(value, dict):
                value = Parsable.parsed_dict(value)
            self.update_property(value, property_name)

    def update_list_of_parsable_property(self, only_if_missing: bool, input_value: dict, property_name: str):
        """
        Retrieves the attribute whose value is a list of Parsable objects from the input dictionary and
        populates the desired attribute if desired.

        Args:
            only_if_missing: bool
                Indicates whether the attribute should be updated only if it does not currently have a value assigned.
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute to populate.
        """
        if only_if_missing:
            if hasattr(self, "has_" + property_name):
                if self.__getattribute__("has_" + property_name):
                    return
        if property_name in input_value:
            value = input_value.get(property_name)
            if isinstance(value, list):
                value = Parsable.parsed_list(value)
            self.update_property(value, property_name)

    def update_specialized_property(self, only_if_missing: bool, input_value: dict, property_name: str):
        """
        Retrieves the attribute whose value requires a specialized decoding function from the input dictionary
        and populates the desired attribute if desired.

        Args:
            only_if_missing: bool
                Indicates whether the attribute should be updated only if it does not currently have a value assigned.
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute to populate.

        Raises:
            AttributeError: 
                If the Parsable subclass does not have a method named ''property_name'_decode'.
        """
        if hasattr(self, property_name + '_decode'):
            if only_if_missing:
                if hasattr(self, "has_" + property_name):
                    if self.__getattribute__("has_" + property_name):
                        return
            if property_name in input_value:
                self.__getattribute__(property_name + '_decode')(input_value.get(property_name))
        else:
            logger.log_and_raise(AttributeError, "Unable to decode attribute [", property_name,
                                 "] since there is no function [", property_name + '_decode', "].")

    ##########################################################################
    # Equality Checks
    ##########################################################################
    def equals(self, other: Parsable, **kwargs) -> bool:
        """Compares whether two Parsable objects are equal in their parsable attributes.

        Args:
            other: Parsable
                The other Parsable to compare to this Parsable.
            **kwargs:
                Additional key-word arguments.

        Returns:
            bool:
                True iff all parsable attributes are equal.
        """
        if type(self) != type(other):
            return False

        for property_name in self.collect_all_attributes():
            self_value, other_value, equals = self.equals_property_name(other, property_name)
            if equals:
                continue
            elif equals is False or not equal(self_value, other_value, **kwargs):
                return False

        return True

    def equals_property_name(self, other: Parsable, property_name: str) -> Tuple[Any, Any, Optional[bool]]:
        """Checks if self and other have a property and get the property if they do.

        Args:
            other: Parsable
                Another Parsable of the same type as self.
            property_name: str
                The name of the property to check.

        Returns:
            Tuple[Any, Any, Optional[bool]]:
                The value of the properties from self + other (if both Parsables had the property) and if we can short
                circuit the evaluation. If the third item in the tuple is not None, we don't need to compare the values.
        """
        if hasattr(self, 'has_' + property_name):
            self_has_property = self.__getattribute__('has_' + property_name)
            other_has_property = other.__getattribute__('has_' + property_name)
            if not self_has_property and not other_has_property:
                return None, None, True
            elif self_has_property != other_has_property:
                return None, None, False

        self_value = self.__getattribute__(property_name)
        other_value = other.__getattribute__(property_name)
        if type(self_value) != type(other_value):
            return None, None, False

        return self_value, other_value, None

    ##########################################################################
    # Serialization and File IO
    ##########################################################################
    def to_json(self) -> Union[dict, str]:
        """Returns the serialized JSON object.

        Returns:
            Union[dict, str]
                Either the dictionary of internally serialized attributes or the string of the serialized representation
                of the entire class.
        """
        return self.to_dict()

    def from_json(self, json_object: Union[dict, str]):
        """Populates the internal attributes from a JSON based representation.

        Args:
            json_object: Union[dict, str]
                Either the serialized dictionary of this class's attributes or a string representation of a JSON
                document.
        """
        if isinstance(json_object, str):
            json_object = io.from_json_string(json_object)
        self.from_dict(json_object)

    def save_to_json(self, file_path: Union[str, Path], **kwargs) -> Path:
        """Saves the internal representation of this class to a desired file path.

        Args:
            file_path: Union[str, Path]
                A file path like object which must contain at least a directory in its value. Valid inputs take the form
                './foo/bar.baz' or '/foo/bar'.
            **kwargs:
                Additional key-word arguments to provide to the JSON writer.

        Returns:
            Path:
                The full Path object representing the location of the final output file.

        Raises:
            RuntimeError:
                If the provided 'file_path' is not formatted correctly.
        """
        # --- parse the file path ---
        path = io.to_path(file_path)
        if path.name == file_path:
            logger.log_and_raise(RuntimeError, "The input file_path [", file_path, "] does not contain a directory.")

        file_dir = path.parent

        # --- provide proper extension ---
        full_path = io.to_path(file_dir / path.name).with_suffix(".json")

        # --- make the directory ---
        io.create_directories(file_dir)

        # --- write the json file ---
        io.write_to_json_file(full_path, self.to_dict(), **kwargs)

        return full_path

    def load_from_json(self, file_path: Union[Path, str], **kwargs):
        """Loads and populates the internal attributes of this subclass from a JSON file.

        Args:
            file_path: Union[Path, str]
                The full path of the JSON file that is to be loaded.
            **kwargs:
                Additional key-word arguments to pass into the JSON reader.

        Raises:
            RuntimeError: If the provided 'file_path' does not point to file that currently exists.
        """
        # --- validate the file path ---
        if not io.file_exists(file_path):
            logger.log_and_raise(RuntimeError, "The file path [", file_path, "] does not exist. Cannot load object.")

        # --- read the json file ---
        json_object = io.read_json_file(file_path, **kwargs)

        # --- create the python object ---
        self.from_json(json_object)
