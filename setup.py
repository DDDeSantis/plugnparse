# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# --- data files for packaging ---
data_files = [("", ["requirements.txt", "README.md"])]

# --- excluded packages ---
excluded_packages = ["tests*"]
included_packages = ["plugnparse*"]

# --- found packages ---
packages = find_packages(where='src', include=included_packages, exclude=excluded_packages)

# --- location of packages ---
package_dirs = {"": "src"}

classifiers = [
      "Programming Language :: Python :: 3.11",
      "Private :: Do Not Upload",
      "Typing :: Typed"
]

# --- setup the package ---
setup(author="Dylan DeSantis",
      description="Python utilities package for plugin style architectures with parsable classes for parameters.s.",
      include_package_data=True,
      data_files=data_files,
      long_description=open("README.md").read(),
      long_description_content_type="text/markdown",
      name="plugnparse",
      packages=packages,
      package_data={"plugnparse": ["py.typed"]},
      package_dir=package_dirs,
      classifiers=classifiers,
      zip_safe=False)