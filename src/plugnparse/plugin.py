from . import properties
import abc
from . import logger
import sys
import importlib
import inspect
import functools
from typing import TypeVar

# import pluggy
# \TODO Look at pluggy for calling entry points.
# \TODO create property decorator that can construct plugins '@plugin_property'
# if sys.version_info < (3, 10):
#     from importlib_metadata import entry_points
# else:
#     from importlib.metadata import entry_points
# import class_registry
from pkg_resources import working_set

# working_set.find_plugins
if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata


# def load_setuptools_entrypoints(self, group, name=None):
#     """Load modules from querying the specified setuptools ``group``.
#
#     :param str group: entry point group to load plugins
#     :param str name: if given, loads only plugins with the given ``name``.
#     :rtype: int
#     :return: return the number of loaded plugins by this call.
#     """
#     count = 0
#     for dist in list(importlib_metadata.distributions()):
#         for ep in dist.entry_points:
#             if (
#                     ep.group != group
#                     or (name is not None and ep.name != name)
#                     # already registered
#                     or self.get_plugin(ep.name)
#                     or self.is_blocked(ep.name)
#             ):
#                 continue
#             plugin = ep.load()
#             self.register(plugin, name=ep.name)
#             self._plugin_distinfo.append((plugin, DistFacade(dist)))
#             count += 1
#     return count

def get_subclass_map(class_type, class_map: dict) -> dict:
    for subclass in class_type.__subclasses__():
        class_map[subclass.__name__] = subclass
        class_map = get_subclass_map(subclass, class_map)
    return class_map


    """
    Parameters used to determine and control the FillStrategy class.
    """
    plugin_property_name = 'strategy_type'
    plugin_module_property_name = 'strategy_module'

class PluginBase(metaclass=abc.ABCMeta):
    _registered_plugins = None

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def add_registry(cls):
        if not hasattr(type(cls), '_registered_plugins'):
            setattr(type(cls), '_registered_plugins', dict())

    @classmethod
    def has_registry(cls):
        return hasattr(type(cls), '_registered_plugins')

    @classmethod
    def has_registered_class(cls, class_name):
        if not cls.has_registry():
            return False
        return class_name in type(cls)._registered_plugins

    @classmethod
    def get_class(cls, class_name, class_module=None, input_values=None):
        if not cls.has_registry():
            cls.add_registry()
        if cls.has_registered_class(class_name):
            return type(cls)._registered_plugins.get(class_name)
        else:
            subclasses = dict()
            subclasses = get_subclass_map(cls, subclasses)
            if class_name in subclasses:
                type(cls)._registered_plugins.update(**subclasses)
                return subclasses.get(class_name)
            else:
                if class_module is None and input_values is None:
                    return None
                elif class_module is None:
                    _, class_module = properties.ParsableProperty.get_class_and_module_strings(input_values,
                                                                                               parsable_class=class_name)
                if class_module is None:
                    return None
                imported_module = importlib.import_module(class_module)
                class_type = getattr(imported_module, class_name)
                subclasses = dict()
                subclasses = get_subclass_map(cls, subclasses)
                if class_type.__name__ in subclasses:
                    type(cls)._registered_plugins.update(**subclasses)
                return class_type

    @classmethod
    def gather_plugin_class_and_module_keywords(cls):
        if type(cls) is type(PluginBase):
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
        else:
            raise RuntimeError(logger.error("Unable to deduce base class plugin properties in this class method "
                                            "when PluginBase is used as the base class. Try using a more specific base"
                                            " class implementation.", record_location=True))

    @classmethod
    def extract_plugin_class_and_module_names(cls, parameters, use_default):
        if use_default:
            plugin_property_name = properties.generic_parsable_type
            plugin_module_property_name = properties.generic_parsable_module
        else:
            plugin_property_name, plugin_module_property_name = cls.gather_plugin_class_and_module_keywords()
        if plugin_property_name is None:
            raise RuntimeError(logger.error("Unable to extract property to indicate the plugin type. Ensure"
                                            " that either the class contains a class variable named "
                                            "'plugin_property_name' which points to the property in the provided "
                                            "parameters object that indicates the plugin name or a class variable "
                                            "named 'parameters_cls' which points to the parameters class "
                                            "which then must contain a valid 'plugin_property_name' "
                                            "class variable. Unable to generate a plugin for class [",
                                            type(cls), "]!", record_location=True))
        if isinstance(parameters, dict):
            if plugin_property_name not in parameters:
                raise RuntimeError(logger.error("Unable to extract plugin property name [",
                                                plugin_property_name, "] from dict object. Unable to generate Plugin!",
                                                record_location=True))
            else:
                class_name = parameters.get(plugin_property_name)

            if plugin_module_property_name is not None:
                if plugin_module_property_name not in parameters:
                    raise RuntimeError(logger.error("Unable to extract plugin module name [",
                                                    plugin_module_property_name,
                                                    "] from dict object. Unable to generate Plugin!",
                                                    record_location=True))
                else:
                    module_name = parameters.get(plugin_module_property_name)
            else:
                module_name = None
        else:
            if not hasattr(type(parameters), plugin_property_name):
                raise RuntimeError(logger.error("Unable to extract plugin property name [",
                                                plugin_property_name, "] from parameters object [",
                                                type(parameters), "]. Unable to generate Plugin!",
                                                record_location=True))
            if hasattr(parameters, 'has_' + plugin_property_name):
                if getattr(parameters, 'has_' + plugin_property_name):
                    class_name = getattr(parameters, plugin_property_name)
                else:
                    raise RuntimeError(logger.error("The plugin property name [", plugin_property_name,
                                                    "] has not been assigned to the provided parameters object [",
                                                    type(parameters), "]. Unable to generate Plugin!",
                                                    record_location=True))
            else:
                class_name = getattr(parameters, plugin_property_name)

            if plugin_module_property_name is not None:
                if hasattr(parameters, 'has_' + plugin_module_property_name):
                    if getattr(parameters, 'has_' + plugin_module_property_name):
                        module_name = getattr(parameters, plugin_module_property_name)
                    else:
                        raise RuntimeError(logger.error("The plugin property name [", plugin_module_property_name,
                                                        "] has not been assigned to the provided parameters object [",
                                                        type(parameters), "]. Unable to generate Plugin!",
                                                        record_location=True))
                else:
                    module_name = getattr(parameters, plugin_module_property_name)
            else:
                module_name = None

        return class_name, module_name

    @classmethod
    def lookup(cls, class_name, class_module, input_values=None):
        output_class = cls.get_class(class_name, class_module, input_values)
        if output_class is None:
            raise RuntimeError(logger.error("Subclass [", class_name, "] is not registered", record_location=True))
        return output_class

    @classmethod
    def construct(cls, class_name, *args, class_module=None, **kwargs):
        return cls.lookup(class_name, class_module, kwargs)(*args, **kwargs)

    @classmethod
    def construct_from_parameters(cls, parameters: object, *args: object, use_default: bool = False,
                                  **kwargs: object):
        class_name, module_name = cls.extract_plugin_class_and_module_names(parameters, use_default)
        return cls.construct(class_name, *args, class_module=module_name, **kwargs)

    @classmethod
    def parse(cls, class_name, *args, class_module=None, **kwargs):
        output_class = cls.lookup(class_name, class_module, kwargs)
        if hasattr(output_class, 'from_dict'):
            output_instance = output_class(*args)
            output_instance.from_dict(kwargs)
            return output_instance
        else:
            raise RuntimeError(logger.error("Class [", output_class.__name__,
                                            "] does not have a function named 'from_dict'", record_location=True))

    @classmethod
    def parse_from_parameters(cls, parameters, *args, use_default=False, **kwargs):
        class_name, module_name = cls.extract_plugin_class_and_module_names(parameters, use_default)
        return cls.parse(class_name, *args, class_module=module_name, **kwargs)
