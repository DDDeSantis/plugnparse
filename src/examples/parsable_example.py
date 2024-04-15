# --- external imports ---
from enum import Enum, auto
from typing import Optional, List, Dict
# --- internal imports ---
from plugnparse import Parsable, enum_setter, properties, logger


class EnumClass(Enum):
    Foo = auto()
    Bar = auto()
    Baz = auto()


class ClassA(Parsable):

    def __init__(self, *args, **kwargs):
        # --- init the parent ---
        super().__init__(*args, **kwargs)
        # --- update the lists of serializable attributes ---
        self._serializable_attributes.extend(['foo'])
        self._enum_attributes.extend(['bar'])
        self._specialized_attributes.extend(['baz'])

        # --- set the properties ---
        self.foo = kwargs.get('foo')
        self.bar = kwargs.get('bar')
        self.baz = kwargs.get('baz')

    ##########################################################################
    # Foo Properties
    ##########################################################################
    @property
    def has_foo(self):
        return self._foo is not None

    @property
    def foo(self) -> int:
        if self._foo is None:
            logger.log_and_raise(AttributeError, "foo has not been set")
        return self._foo

    @foo.setter
    def foo(self, input_value: Optional[int]):
        if input_value is None or isinstance(input_value, int):
            self._foo = input_value
        else:
            logger.log_and_raise(TypeError, "Invalid input type [", type(input_value), "].")

    ##########################################################################
    # Bar Properties
    ##########################################################################
    @property
    def has_bar(self):
        return self._bar is not None

    @property
    def bar(self) -> EnumClass:
        if self._bar is None:
            logger.log_and_raise(AttributeError, "bar has not been set")
        return self._bar

    @bar.setter
    @enum_setter(EnumClass)
    def bar(self, input_value: Optional[EnumClass]):
        if input_value is None or isinstance(input_value, EnumClass):
            self._bar = input_value
        else:
            logger.log_and_raise(TypeError, "Invalid input type [", type(input_value), "].")

    ##########################################################################
    # Baz Properties
    ##########################################################################
    @property
    def has_baz(self):
        return self._baz is not None

    @property
    def baz(self) -> float:
        if self._baz is None:
            logger.log_and_raise(AttributeError, "baz has not been set.")
        return self._baz

    @baz.setter
    def baz(self, input_value: Optional[float]):
        if input_value is None or isinstance(input_value, float):
            self._baz = input_value
        else:
            logger.log_and_raise(TypeError, "Invalid input type [", type(input_value), "].")

    def baz_encode(self) -> dict:
        """Special encoder function for baz"""
        return {"baz_keyword": self.baz}

    def baz_decode(self, input_value: dict):
        """Special decoder function."""
        self.baz = input_value.get('baz_keyword')


class ClassB(Parsable):

    def __init__(self, *args, **kwargs):
        # --- init the parent ---
        super().__init__(*args, **kwargs)
        # --- update the attributes ---
        self._parsable_attributes.extend(['bingo'])
        self._dict_of_parsables.extend(['bingo_dictionary'])
        self._list_of_parsables.extend(['bango_list'])

        # --- set the components ---
        self.bingo = kwargs.get('bingo')
        self.bingo_dictionary = kwargs.get('bingo_dictionary')
        self.bango_list = kwargs.get('bango_list')

    ##########################################################################
    # Bingo Properties
    ##########################################################################
    @property
    def has_bingo(self):
        return self._bingo is not None

    @property
    def bingo(self) -> ClassA:
        if self._bingo is None:
            logger.log_and_raise(AttributeError, "bingo has not been set")
        return self._bingo

    @bingo.setter
    @ClassA.static_class_setter()
    def bingo(self, input_value: Optional[ClassA]):
        if input_value is None or isinstance(input_value, ClassA):
            self._bingo = input_value
        else:
            logger.log_and_raise(TypeError, "Invalid input type [", type(input_value), "].")

    ##########################################################################
    # Bingo Dictionary Properties
    ##########################################################################
    @property
    def has_bingo_dictionary(self):
        return self._bingo_dictionary is not None

    @property
    def bingo_dictionary(self) -> Dict[str, ClassA]:
        if self._bingo_dictionary is None:
            logger.log_and_raise(AttributeError, "bingo_dictionary has not been set")
        return self._bingo_dictionary

    @bingo_dictionary.setter
    def bingo_dictionary(self, input_value: Optional[Dict[str, ClassA]]):
        if input_value is None:
            self._bingo_dictionary = None
        elif isinstance(input_value, dict):
            for key, value in input_value.items():
                if not (isinstance(key, str) and isinstance(value, ClassA)):
                    logger.log_and_raise(TypeError, "Invalid input type [", type(input_value), "].")
            self._bingo_dictionary = input_value
        else:
            logger.log_and_raise(TypeError, "Invalid input type [", type(input_value), "].")

    ##########################################################################
    # Bango List Properties
    ##########################################################################
    @property
    def has_bango_list(self):
        return self._bango_list is not None

    @property
    def bango_list(self) -> List[ClassA]:
        if self._bango_list is None:
            logger.log_and_raise(AttributeError, "bango_list has not been set")
        return self._bango_list

    @bango_list.setter
    def bango_list(self, input_value: Optional[List[ClassA]]):
        if input_value is None:
            self._bango_list = None
        elif isinstance(input_value, list):
            for value in input_value:
                if not isinstance(value, ClassA):
                    logger.log_and_raise(TypeError, "Invalid input type [", type(input_value), "].")
            self._bango_list = input_value
        else:
            logger.log_and_raise(TypeError, "Invalid input type [", type(input_value), "].")


##########################################################################
# Main Example usage
# ##########################################################################
json_dictionary = {'foo': 1, 'bar': "Foo", 'baz': {'baz_keyword': 10.0}}
class_a = ClassA()
class_a.from_dict(json_dictionary)

print(class_a.to_dict())


full_json_dictionary = class_a.to_dict()
new_class_a = properties.parse(full_json_dictionary, throw_if_unable_to_parse=True)
print("parsed type: ", type(new_class_a))
print("parsed information: ", new_class_a.to_dict())


class_b_json_dictionary = {'bingo': {'foo': 1, 'bar': "Foo"},
                           'bingo_dictionary': {'a': {'parsable_type': 'ClassA', 'parsable_module': '__main__', 'foo': 5}},
                           'bango_list': [{'parsable_type': 'ClassA', 'parsable_module': '__main__', 'foo': 10}]}
class_b = ClassB()
class_b.from_dict(class_b_json_dictionary)
print(class_b.to_dict())





