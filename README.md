# Plug-n-Parse
Python utilities package for plugin style architectures with parsable classes for parameters.

- [Setting Up](#setting-up-and-building)
- [Testing](#testing)
- [Coverage](#coverage)

## Setting Up and Building

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