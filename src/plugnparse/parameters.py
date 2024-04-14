# --- external imports ---
from . import parsable


class Parameters(parsable.Parsable):
    """
    Represents the base class of Parameters used for Plugin classes.

    Notes:
        A Parameters class will generally be associated with a specific Plugin base class. To know which plugin to
        generate in a pipeline, two things are needed, the concrete class name, and the location of the module it is
        defined. This information is generally configurable and is most likely provided in a corresponding base
        Parameters class for the specific plugin base class. To know which properties in the Parameters class holds
        this information the property names need to be provided as function of the specific base plugin class.
        The following schema is defined to provide this information:
        - The specific base plugin class has a class attribute named `parameters_cls`. The value of the `parameters_cls`
         attribute is the corresponding specific Parameters base class type. The Parameters class type is then
         expected that have two class attributes:
            1. A class attribute `plugin_property_name` which contains the name of the property in the Parameters class
             whose value is the name of the class of the desired concrete Plugin class.
            2. A class attribute `plugin_module_property_name` which contains the name of the property in the Parameters
             class whose value is the string representation of the module where the desired concrete Plugin class
             is defined.

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
    """

    def __init__(self, *args, **kwargs):
        # --- init the parent ---
        super().__init__(*args, **kwargs)
