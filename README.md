# Plug-n-Parse
Python utilities package for plugin style architectures with parsable classes for parameters.

- [Setting Up](#setting-up)
- [Testing](#testing)
- [Coverage](#coverage)
- [Usage](#usage)

## Setting Up

### Setting Up Local Environment
Install python >3.8 if it is not already installed.

#### Set Up the Virtual Environment
Set up the local environment and install pre-commit so that the hooks are automatically run locally:
```shell
python3 -m  venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Setting Up for the Build
To build the python wheels and distribution package, use the `build` python packages.

To install the `build` package use the following command:

```shell
pip install --upgrade build
```

#### Building the Packages
To execute the build, follow the commands below. More detailed instructions on using `build` can be found [here](https://pypa-build.readthedocs.io/en/latest/).

```shell
python -m build
```

This should generate  `plugnparse-<version>.tar.gz` and `plugnparse-<version>-py3-none-any.whl` files in either the current working 
directory, `<cwd>/dist/`, or to a desired output directory using the argument `--outdir OUTDIR` in the build command 
above. 

#### Installing the Built Packages
Use `pip` to install the generated package in another virtual environment or computer. This can be done using the
following command:

```shell
pip install OUTDIR/plugnparse-<verison>-py3-none-any.whl
```

The `OUTDIR` is the directory location of the generated python wheel.

#### Uploading to PyPi
After building the packages, you will be able to upload the packages to PyPi. This requires that a new version be
created, so any time you wish to upload a new package to PyPi you must increase the plugnparse version number. This is
found in the pyproject.toml file.

To upload the built package use the following command and enter your PyPi token when prompted.
```shell
twine upload dist/*
```

## Testing
To run the tests follow the below commands
```shell
cd plugnparse/src
pytest ./tests
```

## Coverage
To generate coverage reports follow the below commands
```shell
pip install -U coverage
coverage run --rcfile=./.coveragerc -m pytest ./src/tests
coverage html
google-chrome ./artifacts/coverage_report/html/index.html
```

## Usage
- [Using the Parsable Class](#using-the-parsable-class)
- [Using the Plugin and Parameters Classes](#using-the-plugin-and-parameters-classes)

### Using the Parsable Class
The `Parsable` class allows for automatic serialization and deserialization of entire classes in a JSON format.
The following example demonstrates a basic usage of the `Parsable` class.

```python
# --- external imports ---
from enum import Enum, auto
from typing import Optional
# --- internal imports ---
from plugnparse import Parsable, enum_setter, logger


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
```

You should then provide a json dictionary of serializable values with the `from_dict()` function.

```python
json_dictionary = {'foo': 1, 'bar': "Foo", 'baz': {'baz_keyword': 10.0}}
class_a = ClassA()
class_a.from_dict(json_dictionary)
```

To then get the original json dictionary from the updated class you use the `to_dict()` function

```python
print(class_a.to_dict())
>>> {'parsable_type': 'ClassA', 'parsable_module': '__main__', 'foo': 1, 'bar': 'Foo', 'baz': {'baz_keyword': 10.0}}
```

Notice that the additional key-value pairs, `parsable_type` and `parsable_module`. These two key-values allow for generic
creation and parsing directly from the json object without needing to know the class type that is being parsed. To leverage
this type of functionality you can utilize the plugnparse properties module and specifically its `parse()` function.

```python
from plugnparse import properties

full_json_dictionary = class_a.to_dict()
new_class_a = properties.parse(full_json_dictionary)
print("parsed type: ", type(new_class_a))
print("parsed information: ", new_class_a.to_dict())

>>> parsed type:  <class '__main__.ClassA'>
>>> parsed information:  {'parsable_type': 'ClassA', 'parsable_module': '__main__', 'foo': 1, 'bar': 'Foo', 'baz': {'baz_keyword': 10.0}}
```

Once there is a single `Parsable` implementation then other `Parsable` classes can have attributes which can also be `Parsable` types.
The class below demonstrates the additional type of attributes that can be automatically parsed which are:
- Parsable attributes
- A dictionary of parsable key-value pairs, specifically where the values are subclasses of `Parsable`.
- A list of parsable values.

```python
from typing import Dict


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
```

Again to populate the `ClassB`, you would provide it a serialized form of the json dictionary.

```python
class_b_json_dictionary = {'bingo': {'foo': 1, 'bar': "Foo"},
                           'bingo_dictionary': {'a': {'parsable_type': 'ClassA', 'parsable_module': '__main__', 'foo': 5}},
                           'bango_list': [{'parsable_type': 'ClassA', 'parsable_module': '__main__', 'foo': 10}]}
class_b = ClassB()
class_b.from_dict(class_b_json_dictionary)
print(class_b.to_dict())
>>> {'parsable_type': 'ClassB', 'parsable_module': '__main__', 'bingo': {'parsable_type': 'ClassA', 'parsable_module': '__main__', 'foo': 1, 'bar': 'Foo'}, 'bingo_dictionary': {'a': {'parsable_type': 'ClassA', 'parsable_module': '__main__', 'foo': 5}}, 'bango_list': [{'parsable_type': 'ClassA', 'parsable_module': '__main__', 'foo': 10}]}
```

### Using the Plugin and Parameters Classes
Together the `Parameters` and the `Plugin` classes can be utilized to generate a plugin architecture very simply.
The example below demonstrates the bare minimum implementations needed to create a plugin architecture.

```python
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
```

To then utilize the architecture you would populate your parameters class and construct the desired plugins from it.
```python 
parameters = ExampleParameters(plugin_type="PluginExampleA", plugin_module="__main__")
generated_plugin = BasePlugin.construct_from_parameters(parameters)
generated_plugin.execute()
>>> PluginExampleA: Foo!
```

To create a different plugin all you need to do is update the parameters used to generate the plugin (generally the module is also updated but since this code is all in one file the module is the same).

```python
parameters.plugin_type = "PluginExampleB"
second_generated_plugin = BasePlugin.construct_from_parameters(parameters)
second_generated_plugin.execute()
>>> PluginExampleB: Bar!
```
