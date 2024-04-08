# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# --- read requirements.txt ---
with open("requirements.txt") as f:
    install_requires = [line.strip() for line in f.readlines() if line]

# --- data files for packaging ---
data_files = [("", ["requirements.txt", "README.md"])]

# --- excluded packages ---
excluded_packages = ["tests*"]
included_packages = ["plugnparse*"]

# --- found packages ---
packages = find_packages(where='src', include=included_packages, exclude=excluded_packages)

# --- location of packages ---
package_dirs = {"": "src"}

classifiers = ["Programming Language :: Python :: 3.11",
               "Private :: Do Not Upload"]

# --- setup the package ---
setup(author="Dylan DeSantis",
      description="Python utilities package for plugin style architectures with parsable classes for parameters.s.",
      install_requires=install_requires,
      include_package_data=True,
      data_files=data_files,
      long_description=open("README.md").read(),
      long_description_content_type="text/markdown",
      name="plugnparse",
      packages=packages,
      package_dir=package_dirs,
      classifiers=classifiers,
      version="0.1.0",
      zip_safe=False)