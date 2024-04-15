# --- external imports ---
from typing import Optional
from abc import ABC, abstractmethod
# --- internal imports ---
from plugnparse import Plugin, Parameters, logger


class ExampleParameters(Parameters):
    plugin_property_name = 'plugin_type'
    plugin_module_property_name = 'plugin_module'
    
    def __init__(self, *args, **kwargs):
        # --- init the parent ---
        super().__init__(*args, **kwargs)
        # --- update the attributes ---
        self._serializable_attributes.extend(['plugin_type', 'plugin_module'])
        
        # --- set components ---
        self.plugin_type = kwargs.get('plugin_type')
        self.plugin_module = kwargs.get('plugin_module')
        
    ##########################################################################
    # Plugin Type Properties
    ##########################################################################
    @property
    def has_plugin_type(self):
        return self._plugin_type is not None

    @property
    def plugin_type(self) -> str:
        if self._plugin_type is None:
            logger.log_and_raise(AttributeError, "plugin_type has not been set")
        return self._plugin_type

    @plugin_type.setter
    def plugin_type(self, input_value: Optional[str]):
        if input_value is None or isinstance(input_value, str):
            self._plugin_type = input_value
        else:
            logger.log_and_raise(TypeError, "Invalid input type [", type(input_value), "].")

    ##########################################################################
    # Plugin Module Properties
    ##########################################################################
    @property
    def has_plugin_module(self):
        return self._plugin_module is not None

    @property
    def plugin_module(self) -> str:
        if self._plugin_module is None:
            logger.log_and_raise(AttributeError, "plugin_module has not been set")
        return self._plugin_module

    @plugin_module.setter
    def plugin_module(self, input_value: Optional[str]):
        if input_value is None or isinstance(input_value, str):
            self._plugin_module = input_value
        else:
            logger.log_and_raise(TypeError, "Invalid input type [", type(input_value), "].")


class BasePlugin(Plugin, ABC):
    parameters_cls = ExampleParameters

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    ##########################################################################
    # Dynamic Function
    ##########################################################################
    @abstractmethod
    def execute(self):
        pass  # pragma: no cover


class PluginExampleA(BasePlugin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    ##########################################################################
    # Dynamic Function
    ##########################################################################
    def execute(self):
        print("PluginExampleA: Foo!")


class PluginExampleB(BasePlugin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    ##########################################################################
    # Dynamic Function
    ##########################################################################
    def execute(self):
        print("PluginExampleB: Bar!")


##########################################################################
# Main Example usage
# ##########################################################################
parameters = ExampleParameters(plugin_type="PluginExampleA", plugin_module="__main__")

generated_plugin = BasePlugin.construct_from_parameters(parameters)
generated_plugin.execute()

parameters.plugin_type = "PluginExampleB"
second_generated_plugin = BasePlugin.construct_from_parameters(parameters)
second_generated_plugin.execute()