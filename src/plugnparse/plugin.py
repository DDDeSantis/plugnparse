# --- external imports ---
import abc
import importlib
from typing import Optional, Dict, Type, Any, Tuple, Union
# --- internal imports ---
from . import properties, logger


class Plugin(metaclass=abc.ABCMeta):
    """
    Represents the base class for all plugin capable classes.

    Notes:
        The Plugin class allows for users to define more specific abstract base classes. From the specific base classes,
        concrete classes can be developed. To know which plugin to generate in a pipeline, two things are needed, the
        concrete class name, and the location of the module it is defined. This information is generally configurable
        and is most likely provided in a corresponding base Parameters class for the specific plugin base class. To know
        which properties in the Parameters class holds this information the property names need to be provided as
        function of the specific base plugin class.

        The following schema is defined to provide this information:
            1. The specific base plugin class has a class attribute named `parameters_cls`
                - The value of the `parameters_cls` attribute is the corresponding specific Parameters base class type.
                - The Parameters class type is then expected that have two class attributes:
                    1. A class attribute `plugin_property_name` which contains the name of the property in the
                       Parameters class whose value is the name of the class of the desired concrete Plugin class.
                    2. A class attribute `plugin_module_property_name` which contains the name of the property
                       in the Parameters class whose value is the string representation of the module where the
                       desired concrete Plugin class is defined.
            2. The specific base plugin class has two class attributes:
                    1. A class attribute `plugin_property_name` which contains the name of the key-word in a
                       dictionary or a property in the specific Parameters base class whose value is the name of the
                       class of the desired concrete Plugin class.
                    2. A class attribute `plugin_module_property_name` which contains the name of the key-word in a
                       dictionary or a property in the specific base Parameters class whose value is the string
                       representation of the module where the desired concrete Plugin class is defined.

    Examples:
        - An example of a specific base plugin class, `Foo`, with a corresponding base parameters, `FooParameters`.

        ---

        from plugnparse.plugin import Plugin
        from plugnparse.parameters import Parameters

        class FooParameters(Parameters):
            plugin_property_name = 'foo_type'
            plugin_module_property_name = 'foo_module'

            def __init__(self, foo_type, foo_module):
                # --- init the parent ---
                super().__init__()
                # --- set up the parsable attributes ---
                self._serialized_attributes.extend(['foo_type', 'foo_module'])

                # --- set components ---
                self.foo_type = foo_type
                self.foo_module = foo_module

            def has_foo_type(self):
                ...
            @property
            def foo_type(self):
                ...
            @foo_type.setter
            def foo_type(self, value):
                ...

            def has_foo_module(self):
                ...
            @property
            def foo_module(self):
                ...
            @foo_module.setter
            def foo_module(self, value):
                ...



        class Foo(Plugin):
            parameters_cls = Properties

            def __init__(self, *args, **kwargs):
                ...

        ---

        - An example of a specific base plugin class, `Foo` which define its own class properties.

        ---

        from plugnparse.plugin import Plugin


        class Foo(Plugin):
            plugin_property_name = 'foo_type'
            plugin_module_property_name = 'foo_module'

            def __init__(self, *args, **kwargs):
                ...

        ---
    """
    _registered_plugins: Optional[Dict[str, Type[Any]]] = None

    def __init__(self, *args, **kwargs):
        pass

    ##########################################################################
    # Registry Class Methods
    ##########################################################################
    @classmethod
    def add_registry(cls):
        """Adds an empty dictionary to the internal class type is None is present."""
        if not hasattr(type(cls), '_registered_plugins'):
            setattr(type(cls), '_registered_plugins', dict())

    @classmethod
    def has_registry(cls) -> bool:
        """Returns whether this class type has an internal registry of plugins.

        Returns:
            bool:
                Returns true if this class instance has an internal registry of plugins, false otherwise.
        """
        return hasattr(type(cls), '_registered_plugins')

    @classmethod
    def has_registered_class(cls, class_name: str) -> bool:
        """Returns whether this class type has registered plugin with the provided name.

        Args:
            class_name: str
                The name of the registered plugin.

        Returns:
            bool:
                True if this class type has registered plugin with the provided name, false otherwise.
        """
        if not cls.has_registry():
            return False
        return class_name in type(cls)._registered_plugins

    ##########################################################################
    # Class Extraction and Lookup Methods
    ##########################################################################
    @classmethod
    def lookup(cls,
               class_name: str,
               class_module: Optional[str]) -> Type[Any]:
        """Attempts to find the class plugin with the provided inputs.

        Args:
            class_name: str
                The name of the class to look up.
            class_module: Optional[str]
                The optional module of the class if the plugin is not currently registered.

        Returns:
            Type[Any]:
                The class type of the provided class name.

        Raises:
            RuntimeError:
                If the class type is not registered for the provided class name.
        """
        output_class = cls.get_class(class_name, class_module)
        if output_class is None:
            logger.log_and_raise(RuntimeError, "Subclass [", class_name, "] is not registered")
        return output_class

    @classmethod
    def get_class(cls,
                  class_name: str,
                  class_module: Optional[str]) -> Optional[Type[Any]]:
        """Attempts to find the class plugin type with the provided inputs.

        Args:
            class_name: str
                The name of the class to look up.
            class_module: Optional[str]
                The optional module of the class if the plugin is not currently registered.

        Returns:
            Optional[Type[Any]]:
                The class type of the provided class name. None is returned if the class type cannot be found.
        """
        # -- initialize the registry if it doesn't exist ---
        if not cls.has_registry():
            cls.add_registry()

        # --- check to see if the class exists already in the registry ---
        if cls.has_registered_class(class_name):
            return type(cls)._registered_plugins.get(class_name)

        # --- update the class with its own subclasses ---
        subclasses = dict()
        subclasses = properties.get_subclass_map(cls, subclasses)

        # --- check to see if the plugin was in the current classes parent tree ---
        if class_name in subclasses:
            type(cls)._registered_plugins.update(**subclasses)
            return subclasses.get(class_name)

        # --- ensure the class module is provided ---
        if class_module is None:
            return None

        # --- import the module ---
        imported_module = importlib.import_module(class_module)

        try:
            # --- extract the class from the module ---
            class_type = getattr(imported_module, class_name)
        except AttributeError as error:
            logger.info("Unable to find the class type for [", class_name, "] in module [", class_module, "]")
            return None

        # --- register the class and its subclasses ---
        subclasses = dict()
        subclasses = properties.get_subclass_map(cls, subclasses)
        if class_type.__name__ in subclasses:
            type(cls)._registered_plugins.update(**subclasses)

        # --- return the class ---
        return class_type

    @classmethod
    def gather_plugin_class_and_module_keywords(cls) -> Tuple[Optional[str], Optional[str]]:
        """Attempts to gather the plugin class and module keywords.

        Notes:
            This requires that the `cls` has one of the following situations for its class attributes:
                1. The `cls` has a class attribute named `parameters_cls`
                    - The value of the `parameters_cls` attribute is Parameters class type.
                    - The Parameters class type is then expected that have two class attributes:
                        1. A class attribute `plugin_property_name` which contains the name of the property in the
                           Parameters class whose value is the name of the class of the desired Plugin class.
                        2. A class attribute `plugin_module_property_name` which contains the name of the property
                           in the Parameters class whose value is the string representation of the module where the
                           desired Plugin class is defined.
                2. The `cls` has two class attributes:
                        1. A class attribute `plugin_property_name` which contains the name of the key-word in a
                           dictionary or a property in a Parameters class whose value is the name of the class of the
                           desired Plugin class.
                        2. A class attribute `plugin_module_property_name` which contains the name of the key-word in a
                           dictionary or a property in a Parameters class whose value is the string representation
                           of the module where the desired Plugin class is defined.

        Returns:
            Tuple[Optional[str], Optional[str]]:
                The plugin class and module keywords as strings. None is returned for the class name or
                the module name if there were unable to be found.
        """
        plugin_property_name = None
        plugin_module_property_name = None
        if hasattr(cls, 'parameters_cls'):
            if hasattr(cls.parameters_cls, 'plugin_property_name'):
                plugin_property_name = cls.parameters_cls.plugin_property_name
            if hasattr(cls.parameters_cls, 'plugin_module_property_name'):
                plugin_module_property_name = cls.parameters_cls.plugin_module_property_name
        else:
            if hasattr(cls, 'plugin_property_name'):
                plugin_property_name = cls.plugin_property_name
            if hasattr(cls, 'plugin_module_property_name'):
                plugin_module_property_name = cls.plugin_module_property_name
        return plugin_property_name, plugin_module_property_name

    @classmethod
    def extract_plugin_class_and_module_names(cls,
                                              parameters: Union[Any, dict],
                                              use_default: bool) -> Tuple[str, str]:
        """Extracts the plugin class and module names from the parameters input.

        Args:
            parameters: Union[Any, dict]
                The parameters from which the plugin class and module will be extracted.
            use_default: bool
                Indicates whether the property names in the parameters input use generic parsable property names to
                identify the class and module names. In this case, almost always the parameters input will be a
                dictionary with the plugin class being derived from Parsable.

        Returns:
            Tuple[str, str]:
                The plugin class and module names, respectively.

        Raises:
            RuntimeError:
                If any of the following conditions occur:
                    - The property for the plugin class cannot be determined.
                    - The property for the module cannot be determined.
                    - The value for the plugin class is not present in the parameters input.
                    - The value for the module name is not present in the parameters input.
        """
        # --- extract which keyword/property names to use for extracting the plugin information ---
        if use_default:
            plugin_property_name = properties.generic_parsable_type
            plugin_module_property_name = properties.generic_parsable_module
        else:
            plugin_property_name, plugin_module_property_name = cls.gather_plugin_class_and_module_keywords()

        # --- ensure that the plugin property name is not none ---
        if plugin_property_name is None:
            logger.log_and_raise(RuntimeError,
                                 "Unable to extract the property to indicate the plugin type. Ensure",
                                 " that either the class contains a class variable named ",
                                 "'plugin_property_name' which points to the property in the provided ",
                                 "parameters object that indicates the plugin name or a class variable ",
                                 "named 'parameters_cls' which points to the parameters class ",
                                 "which then must contain a valid 'plugin_property_name' ",
                                 "class variable. Unable to generate a plugin for class [", type(cls), "]!")

        if plugin_module_property_name is None:
            logger.log_and_raise(RuntimeError,
                                 "Unable to extract the property to indicate the plugin module. Ensure",
                                 " that either the class contains a class variable named ",
                                 "'plugin_module_property_name' which points to the property in the provided ",
                                 "parameters object that indicates the plugin module or a class variable ",
                                 "named 'parameters_cls' which points to the parameters class ",
                                 "which then must contain a valid 'plugin_module_property_name' ",
                                 "class variable. Unable to generate a plugin for class [", type(cls), "]!")

        # --- determine whether the input is a dictionary or a different class object
        if isinstance(parameters, dict):
            # --- raise an exception if the property is not in the dictionary ---
            if plugin_property_name not in parameters:
                logger.log_and_raise(RuntimeError, "Unable to extract plugin property name [",
                                     plugin_property_name, "] from dictionary object. Unable to generate Plugin!")

            # --- assign the class name from the property ---
            class_name = parameters.get(plugin_property_name)

            # --- raise an exception if the property is not in the dictionary ---
            if plugin_module_property_name not in parameters:
                logger.log_and_raise(RuntimeError, "Unable to extract plugin property name [",
                                     plugin_module_property_name, "] from dictionary object. ",
                                     "Unable to generate Plugin!")
            # --- assign the module name from the property ---
            module_name = parameters.get(plugin_module_property_name)
        else:
            # --- ensure the parameters object has a property holding the plugin class name ---
            try:
                # --- assign the class name from the parameters ---
                class_name = getattr(parameters, plugin_property_name)
            except:
                logger.log_and_raise(RuntimeError, "Unable to extract plugin property name [",
                                     plugin_property_name, "] from parameters object [", type(parameters),
                                     "]. Unable to generate Plugin!")

            # --- ensure the parameters object has a property holding the plugin module name ---
            try:
                # --- assign the module name from the parameters ---
                module_name = getattr(parameters, plugin_module_property_name)
            except:
                logger.log_and_raise(RuntimeError, "Unable to extract plugin property name [",
                                     plugin_module_property_name, "] from parameters object [", type(parameters),
                                     "]. Unable to generate Plugin!")

        return class_name, module_name

    ##########################################################################
    # Class Creation Methods
    ##########################################################################
    @classmethod
    def construct(cls, class_name: str, class_module: Optional[str], *args, **kwargs) -> Any:
        """Constructs a class instance with optional initialization arguments.

        Args:
            class_name: str
                The name of the class to be constructed.
            class_module: Optional[str]
                The optional module of the class if the plugin is not currently registered. It is recommended that this
                value always be provided unless it can be guaranteed that the class is already registered.
            *args:
                Additional positional arguments passed to the constructor of the class.
            **kwargs:
                Additional keyword arguments passed to the constructor of the class.

        Returns:
            Any:
                The constructed class.
        """
        return cls.lookup(class_name, class_module)(*args, **kwargs)

    @classmethod
    def construct_from_parameters(cls, parameters: Union[Any, dict], *args, use_default: bool = False, **kwargs) -> Any:
        """Extract the plugin class name and construct the class type with optional initialization arguments.

        Args:
            parameters: Union[Any, dict]
                The parameters from which the plugin class and module will be extracted.
            *args:
                Additional positional arguments passed to the constructor of the class.
            use_default: bool
                Indicates whether the property names in the parameters input use generic parsable property names to
                identify the class and module names (defaults to False).
            **kwargs:
                Additional keyword arguments passed to the constructor of the class.

        Returns:
            Any:
                The constructed class.
        """
        class_name, module_name = cls.extract_plugin_class_and_module_names(parameters, use_default)
        return cls.construct(class_name, module_name, *args, **kwargs)

    @classmethod
    def parse(cls, class_name: str, class_module: Optional[str], *args, **kwargs) -> Any:
        """Constructs a class instance with optional initialization arguments and parses additional information.

        Args:
            class_name: str
                The name of the class to be constructed.
            class_module: Optional[str]
                The optional module of the class if the plugin is not currently registered. It is recommended that this
                value always be provided unless it can be guaranteed that the class is already registered.
            *args:
                Additional positional arguments passed to the constructor of the class.
            **kwargs:
                The keyword arguments to parse into the constructed class.

        Returns:
            Any:
                The constructed class with the additional information parsed into it.

        Raises:
            RuntimeError:
                If the registered class does not have a function named `from_dict()`.
        """
        output_class = cls.lookup(class_name, class_module)
        if hasattr(output_class, 'from_dict'):
            output_instance = output_class(*args)
            output_instance.from_dict(kwargs)
            return output_instance
        logger.log_and_raise(RuntimeError, "Class [", output_class.__name__,
                             "] does not have a function named 'from_dict' and there cannot parse the kwargs")

    @classmethod
    def parse_from_parameters(cls, parameters: Union[Any, dict], *args, use_default: bool = False, **kwargs) -> Any:
        """Extract the plugin class name and construct the class type with optional initialization arguments and
        parses in additional information.

        Args:
            parameters: Union[Any, dict]
                The parameters from which the plugin class and module will be extracted.
            *args:
                Additional positional arguments passed to the constructor of the class.
            use_default: bool
                Indicates whether the property names in the parameters input use generic parsable property names to
                identify the class and module names (defaults to False).
            **kwargs:
                The keyword arguments to parse into the constructed class.

        Returns:
            Any:
                The constructed class with the additional information parsed into it.
        """
        class_name, module_name = cls.extract_plugin_class_and_module_names(parameters, use_default)
        return cls.parse(class_name, module_name, *args, **kwargs)
