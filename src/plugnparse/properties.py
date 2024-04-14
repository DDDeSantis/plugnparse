# --- external imports ---
from enum import Enum
from typing import List, Optional, Type, Union, Any, Tuple, Callable
import importlib
import inspect
import functools
# --- local imports ---
from . import logger

generic_parsable_type = "parsable_type"
generic_parsable_module = "parsable_module"


##########################################################################
# Property Methods and Helpers
##########################################################################
def required_parameter_for_class_init(class_type: Type[Any]) -> List[str]:
    """Returns the required parameter names for initializing the provided class type.

    Args:
        class_type: Type[Any]
            The class type in which to inspect.

    Returns:
        List[str]:
            The list of parameter names that the initialization expects.
    """
    required_args = set()
    signature = inspect.signature(class_type.__init__)
    for name, parameter in signature.parameters.items():
        if parameter.default == parameter.empty and parameter.name != "self" and parameter.kind not in (
                parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
            required_args.add(parameter.name)
    for base in class_type.__bases__:
        required_args = required_args.union(set(required_parameter_for_class_init(base)))
    return list(required_args)


def get_subclass_map(class_type: Type[Any], class_map: dict) -> dict:
    """Returns the subclass map for the provided class type.

    Args:
        class_type: Type[Any]
            The class type in which to inspect.
        class_map: dict
            The subclass map for the provided class type.

    Returns:
        dict:
            The subclass map for the provided class type.
    """
    for subclass in class_type.__subclasses__():
        class_map[subclass.__name__] = subclass
        class_map = get_subclass_map(subclass, class_map)
    return class_map


def get_all_properties(class_type: Type[Any], more_properties: dict) -> dict:
    """Gets all the properties of the provided class type.

    Args:
        class_type: Type[Any]
            The class type in which to inspect.
        more_properties:
            The set of properties to update with the class properties.

    Returns:
        dict:
            The properties of the provided class type and the properties of the provided input dictionary.

    """
    more_properties.update(class_type.__dict__)
    for base in class_type.__bases__:
        more_properties = get_all_properties(base, more_properties)
    return more_properties


def is_property(class_type: Type[Any], property_name: str) -> bool:
    """Checks if a certain property exists in the provided class.

    Args:
        class_type: Type[Any]
            The class type in which to inspect.
        property_name: str
            The name of the property to check for existence.

    Returns:
        bool:
            True if the property exists, False otherwise.
    """
    if not isinstance(class_type, type):
        class_type = type(class_type)
    value = get_all_properties(class_type, dict()).get(property_name)
    return isinstance(value, property)


def get_property(class_type: Type[Any], property_name: str) -> property:
    """Gets a certain property from the provided class.

    Args:
        class_type: Type[Any]
            The class type in which to inspect.
        property_name: str
            The name of the property to get.

    Returns:
        property:
            The property of the class.

    Raises:
        TypeError:
            If the class attribute is not a property.
    """
    if not isinstance(class_type, type):
        class_type = type(class_type)
    value = get_all_properties(class_type, dict()).get(property_name)
    if not isinstance(value, property):
        logger.log_and_raise(TypeError, '{.__name__}.{} is not a property its a '.format(class_type, property_name),
                             type(value), " and the object has ", get_all_properties(class_type, dict()))
    return value


def can_get(class_type: Type[Any], property_name: str) -> bool:
    """Checks if a certain property in the provided class type has the ability to be retrieved.

    Args:
        class_type: Type[Any]
            The class type in which to inspect.
        property_name: str
            The name of the property to check.

    Returns:
        bool:
            True if the property has the ability to be retrieved, False otherwise.
    """
    return get_property(class_type, property_name).fget is not None


def can_set(class_type: Type[Any], property_name: str) -> bool:
    """Checks if a certain property in the provided class type has the ability to be set.

    Args:
        class_type: Type[Any]
            The class type in which to inspect.
        property_name: str
            The name of the property to check.

    Returns:
        bool:
            True if the property has the ability to be set, False otherwise.
    """
    return get_property(class_type, property_name).fset is not None


def can_del(class_type: Type[Any], property_name: str) -> bool:
    """Checks if a certain property in the provided class type has the ability to be deleted.

    Args:
        class_type: Type[Any]
            The class type in which to inspect.
        property_name: str
            The name of the property to check.

    Returns:
        bool:
            True if the property has the ability to be deleted, False otherwise.
    """
    return get_property(class_type, property_name).fdel is not None


##########################################################################
# Parsing Property Methods
##########################################################################
def get_class_and_module_strings(input_value: dict,
                                 parsable_module: Optional[str] = None,
                                 parsable_class: Optional[str] = None,
                                 parsable_module_keyword: str = generic_parsable_module,
                                 parsable_class_keyword: str = generic_parsable_type,
                                 throw_if_unable_to_parse: bool = False) -> Tuple[str, str]:
    """Extracts the class and module strings from the provided dictionary.

    Args:
        input_value: dict
            The dictionary to extract the class and module strings.
        parsable_module: Optional[str]
            The explicit value of the module string to use directly instead of searching in the dictionary.
        parsable_class: Optional[str]
            The explicit value of the class string to use directly instead of searching in the dictionary.
        parsable_module_keyword: str
            The keyword that maps to the module string in the dictionary (default: generic_parsable_module).
        parsable_class_keyword: str
            The keyword that maps to the class string in the dictionary (default: generic_parsable_type).
        throw_if_unable_to_parse: bool
            If true, throws an exception if the class or module string cannot be found (default: False).

    Returns:
        Tuple[str, str]:
            The class and module string values, respectively.

    Raises:
        RuntimeError:
            If the class or module string cannot be found and throw_if_unable_to_parse is True.
    """
    module_str = None
    class_str = None
    # --- find the module to load ---
    if parsable_module is not None:
        if not isinstance(parsable_module, str):
            msg = logger.error("Unable to use type [", type(parsable_module),
                               "] as a string-based name for loading the parsable module.", record_location=True)
            if throw_if_unable_to_parse:
                raise RuntimeError(msg)
        else:
            module_str = parsable_module
    elif parsable_module_keyword in input_value:
        module_str = input_value[parsable_module_keyword]
    else:
        msg = logger.error("Unable to deduce the module name to load for parsing.", module_str,
                           record_location=True)
        if throw_if_unable_to_parse:
            raise RuntimeError(msg)

    # --- find the class to load ---
    if parsable_class is not None:
        if not isinstance(parsable_class, str):
            msg = logger.error("Unable to use type [", type(parsable_class),
                               "] as a string-based name for loading the parsable class.", record_location=True)
            if throw_if_unable_to_parse:
                raise RuntimeError(msg)
        else:
            class_str = parsable_class
    elif parsable_class_keyword in input_value:
        class_str = input_value[parsable_class_keyword]
    else:
        msg = logger.error("Unable to deduce the class name to load for parsing.", record_location=True)
        if throw_if_unable_to_parse:
            raise RuntimeError(msg)

    return class_str, module_str


def get_class_type(input_value: dict,
                   parsable_module: Optional[str] = None,
                   parsable_class: Optional[str] = None,
                   parsable_module_keyword: str = generic_parsable_module,
                   parsable_class_keyword: str = generic_parsable_type,
                   throw_if_unable_to_parse: bool = False,
                   class_type: Optional[Type[Any]] = None) -> Optional[Type[Any]]:
    """Extracts the class type from the provided inputs.

    Args:
        input_value: dict
            The dictionary to extract the class information from.
        parsable_module: Optional[str]
            The explicit value of the module string to use directly instead of searching in the dictionary.
        parsable_class: Optional[str]
            The explicit value of the class string to use directly instead of searching in the dictionary.
        parsable_module_keyword: str
            The keyword that maps to the module string in the dictionary (default: generic_parsable_module).
        parsable_class_keyword: str
            The keyword that maps to the class string in the dictionary (default: generic_parsable_type).
        throw_if_unable_to_parse: bool
            If true, throws an exception if the class type cannot be found (default: False).
        class_type: Optional[Type[Any]]
            The optional class type to use directly instead of searching.

    Returns:
        Optional[Type[Any]]:
            The type of the class specified from the inputs. If the type cannot be found and throw_if_unable_to_parse
            is False, then None is returned.

    Raises:
        RuntimeError:
            If the class type cannot be found and throw_if_unable_to_parse is True.
    """
    if class_type is None:
        class_str, module_str = get_class_and_module_strings(input_value,
                                                             parsable_module,
                                                             parsable_class,
                                                             parsable_module_keyword,
                                                             parsable_class_keyword,
                                                             throw_if_unable_to_parse)
        # --- load in the class ---
        if module_str is not None and class_str is not None:
            try:
                imported_module = importlib.import_module(module_str)
                class_type = getattr(imported_module, class_str)
            except BaseException as error:
                msg = logger.error("Unable to construct parsable object [", class_str,
                                   "] in module [", module_str,
                                   "]. Encountered error: [", error, "]", record_location=True)
                if throw_if_unable_to_parse:
                    raise RuntimeError(msg)
                class_type = None

    return class_type


def get_required_arguments_for_init(class_type: Type[Any], input_dict: dict) -> dict:
    """Extracts the required arguments for the initialization function.

    Args:
        class_type: Type[Any]
            The class type to extract the required arguments for.
        input_dict: dict
            The dictionary to extract the required arguments from.

    Returns:
        dict:
            The mapping of argument names to their values to be used in the initialization function.

    Raises:
        RuntimeError:
            If all the required arguments needed for initialization are not specified in the dictionary.
    """
    required_args = required_parameter_for_class_init(class_type)
    if not all(arg in input_dict for arg in required_args):
        logger.log_and_raise(RuntimeError, "The required arguments ", required_args,
                             " are not included in the provided arguments ", list(input_dict.keys()), ".")
    return dict((k, input_dict[k]) for k in required_args)


def parse(input_value: dict,
          parsable_module: Optional[str] = None,
          parsable_class: Optional[str] = None,
          parsable_module_keyword: str = generic_parsable_module,
          parsable_class_keyword: str = generic_parsable_type,
          throw_if_unable_to_parse: bool = False,
          class_type: Optional[type] = None) -> Union[Type[Any], dict]:
    """Parses the input dictionary and returns the parsed class.

    Args:
        input_value: dict
            The dictionary to parse the class information from.
        parsable_module: Optional[str]
            The explicit value of the module string to use directly instead of searching in the dictionary.
        parsable_class: Optional[str]
            The explicit value of the class string to use directly instead of searching in the dictionary.
        parsable_module_keyword: str
            The keyword that maps to the module string in the dictionary (default: generic_parsable_module).
        parsable_class_keyword: str
            The keyword that maps to the class string in the dictionary (default: generic_parsable_type).
        throw_if_unable_to_parse: bool
            If true, throws an exception if the class type cannot be found or the dictionary cannot be parsed
            (default: False).
        class_type: Optional[Type[Any]]
            The optional class type to use directly instead of searching.

    Returns:
        Optional[Type[Any]]:
            The parsed class type specified from the inputs. If the type cannot be found or the dictionary cannot
             be parsed and throw_if_unable_to_parse is False, then None is returned.

    Raises:
        RuntimeError:
            If the class type cannot be found or the dictionary cannot be parsed and throw_if_unable_to_parse is True.
    """
    # --- find the class type ---
    class_type = get_class_type(input_value,
                                parsable_module,
                                parsable_class,
                                parsable_module_keyword,
                                parsable_class_keyword,
                                throw_if_unable_to_parse,
                                class_type)
    if class_type is not None:
        try:
            required_args = get_required_arguments_for_init(class_type, input_value)
            output = class_type(**required_args)
            output.from_dict(input_value)
            input_value = output
        except BaseException as error:
            msg = logger.error("Unable to construct parsable object [", class_type,
                               "]. Encountered error: [", error, "]", record_location=True)
            if throw_if_unable_to_parse:
                raise RuntimeError(msg)
    return input_value


def enum_parse(enum_type: Type[Enum],
               input_value: Union[str, int, List[Union[str, int]]]) -> Union[Optional[Enum], List[Enum]]:
    """Turns a string, integer, or list of strings or integers into the related enums based on the Enum type passed in.

    Args:
        enum_type: Type[Enum]
            A subclass type of Enum
        input_value: Union[str, int, List[Union[str, int]]]
            Either a string, integer, or list of string or integers

    Returns:
        Union[Optional[Enum], List[Enum]]
            Either the appropriate instance of the given enum type (or None), or a list of instances of given enum type

    Raises:
        TypeError:
            If the given input value cannot be converted to an enum instance, either:
                The int passed is not within the bounds of the enum.
                The string passed does not correlate to an instance of the enum.
                One of the items in the list passed does not correlate to an instance of the enum.
                The type passed in can not be converted to an enum.
    """
    if isinstance(input_value, list):
        return [enum_parse(enum_type, x) for x in input_value]
    if isinstance(input_value, enum_type) or input_value is None:
        return input_value
    elif isinstance(input_value, str):
        try:
            converted_value = enum_type[input_value]
        except KeyError:
            logger.log_and_raise(TypeError, f"{input_value} is not a valid name of a {enum_type}")
    elif isinstance(input_value, int):
        try:
            converted_value = enum_type(input_value)
        except ValueError:
            logger.log_and_raise(TypeError, f"Index {input_value} is not a valid index of a {enum_type}")
    else:
        logger.log_and_raise(TypeError, f"{input_value} can not be converted to {enum_type}")

    return converted_value


##########################################################################
# Decorators
##########################################################################
def enum_setter(enum_type: Type[Enum]) -> Callable[[Any], Any]:
    """Decorator that parses an input into an Enum of the provided type.

    Args:
        enum_type: Type[Enum]
            The type of Enum to parse.

    Returns:
        Callable[[Any], Any]:
            The functor used to parse the given enum type when setting a property
    """

    def decorator_enum_setter(func):
        @functools.wraps(func)
        def wrapper(self, input_value):
            converted_value = enum_parse(enum_type, input_value)
            func(self, converted_value)

        return wrapper

    return decorator_enum_setter


def parsable_setter(parsable_module: Optional[str] = None,
                    parsable_class: Optional[str] = None,
                    parsable_module_keyword: str = generic_parsable_module,
                    parsable_class_keyword: str = generic_parsable_type,
                    throw_if_unable_to_parse: bool = False,
                    class_type: Optional[Type[Any]] = None) -> Callable[[Any], Any]:
    """Decorator that creates a specific Parsable class instance and parses an input dictionary input into it.

    Args:
        parsable_module: Optional[str]
            The explicit value of the module string to use directly instead of searching in the dictionary.
        parsable_class: Optional[str]
            The explicit value of the class string to use directly instead of searching in the dictionary.
        parsable_module_keyword: str
            The keyword that maps to the module string in the dictionary (default: generic_parsable_module).
        parsable_class_keyword: str
            The keyword that maps to the class string in the dictionary (default: generic_parsable_type).
        throw_if_unable_to_parse: bool
            If true, throws an exception if the class type cannot be found or the dictionary cannot be parsed
            (default: False).
        class_type: Optional[Type[Any]]
            The optional class type to use directly instead of searching.

    Returns:
        Callable[[Any], Any]:
            The functor used to parse the given class type when setting a property.
    """

    def decorator_parsable_setter(func):
        @functools.wraps(func)
        def parsable_parse(self, input_value):
            if isinstance(input_value, dict):
                input_value = parse(input_value,
                                    parsable_module,
                                    parsable_class,
                                    parsable_module_keyword,
                                    parsable_class_keyword,
                                    throw_if_unable_to_parse,
                                    class_type)
            func(self, input_value)

        return parsable_parse

    return decorator_parsable_setter
