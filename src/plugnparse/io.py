# --- external imports ---
import os
import tempfile
from typing import Union, List
from pathlib import Path
from datetime import datetime
from distutils.dir_util import copy_tree
import json


##########################################################################
# File and Directory IO
##########################################################################
def file_exists(filepath: Union[str, Path]) -> bool:
    """Checks if a file exists on the filesystem.

    Args:
        filepath: Union[str, Path]
            The path to the file to check.

    Returns:
        bool:
            True if file exists, False otherwise.
    """
    if isinstance(filepath, Path):
        if filepath.exists():
            return True
    elif isinstance(filepath, str):
        if os.path.exists(filepath):
            return True
    return False


def is_directory(filepath: Union[str, Path]) -> bool:
    """ Checks if a directory exists on the filesystem.

    Args:
        filepath: Union[str, Path]
            The path to the directory to check.

    Returns:
        bool:
            True if directory exists, False otherwise.
    """
    if isinstance(filepath, Path):
        if filepath.exists() and filepath.is_dir():
            return True
    elif isinstance(filepath, str):
        if os.path.exists(filepath) and os.path.isdir(filepath):
            return True
    return False


def to_path(file_path: Union[str, Path]) -> Path:
    """ Converts a string to a Path object."""
    if isinstance(file_path, Path):
        return file_path
    else:
        return Path(file_path)


def create_directories(filepath: Union[str, Path]):
    """Creates directories if they don't exist on the filesystem.

    Args:
        filepath: Union[str, Path]
            The path to the directory to create.
    """
    if isinstance(filepath, Path):
        if not filepath.exists() and filepath.suffix == "":
            os.makedirs(filepath)
    elif isinstance(filepath, str):
        if not os.path.exists(filepath):
            os.makedirs(filepath)


def get_temporary_directory() -> Path:
    """Gets the temporary directory.

    Returns:
        Path:
            The path to the temporary directory.
    """
    return Path(tempfile.gettempdir())


def get_all_subdirectories_of_directory(directory: Union[str, Path]) -> List[Path]:
    """Gets all subdirectories of a directory.

    Args:
        directory: Union[str, Path]
            The path to the directory.

    Returns:
        List[Path]:
            The list of all subdirectories of a directory.
    """
    result = []
    for file in os.listdir(directory):
        joined_file = os.path.join(directory, file)
        if is_directory:
            result.append(Path(joined_file))
    return result


def get_most_recently_created_subdirectory(parent_directory: Union[str, Path]) -> Path:
    """Gets the most recently created subdirectory.

    Args:
        parent_directory: Union[str, Path]
            The path to the parent directory.

    Returns:
        Path:
            The path to the most recently created subdirectory.
    """
    all_subdirectories = get_all_subdirectories_of_directory(parent_directory)
    latest_directory = max(all_subdirectories, key=os.path.getctime)
    return latest_directory


def copy_directory_contents_to(original_directory: Union[str, Path], destination_directory: Union[str, Path]):
    """Copies contents of a directory to another directory.

    Args:
        original_directory: Union[str, Path]
            The path to the original directory.
        destination_directory: Union[str, Path]
            The path to the destination directory.
    """
    create_directories(destination_directory)
    copy_tree(original_directory, destination_directory)


##########################################################################
# Datatime
##########################################################################
def get_date_time_string(formatting: str = "%Y_%m_%d-%H_%M_%S"):
    """Returns a string representation of the current datetime.

    Args:
        formatting: str
            The formatting string to use.

    Returns:
        str:
            The string representation of the current datetime.
    """
    now = datetime.now()
    return now.strftime(formatting)


##########################################################################
# Read and Writing
##########################################################################
def read_json_file(file: Union[str, Path], **kwargs) -> dict:
    """Reads a JSON file and returns a dictionary.

    Args:
        file: Union[str, Path]
            The file to read.
        **kwargs:
            Additional keyword arguments to pass to json.loads.

    Returns:
        dict:
            A python dictionary.
    """
    with open(str(file), "r") as f:
        return json.load(f, **kwargs)


def write_to_json_file(file: Union[str, Path], parsable_dictionary: dict, **kwargs):
    """Writes a dictionary to a JSON file.

    Args:
        file: Union[str, Path]
            The file to write to.
        parsable_dictionary: dict
            The dictionary to write.
        **kwargs:
            Additional keyword arguments to pass to json.dumps.
    """
    with open(str(file), "w") as f:
        json.dump(parsable_dictionary, f, **kwargs)


##########################################################################
# Serialization
##########################################################################
def from_json_string(input_string: str, **kwargs) -> dict:
    """Converts a JSON string to a Python dictionary.

    Args:
        input_string: str
            The string to convert.
        **kwargs:
            Additional keyword arguments to pass to json.loads.

    Returns:
        dict:
            A python dictionary.
    """
    return json.loads(input_string, **kwargs)


def to_json_string(parsable_dictionary: dict, **kwargs) -> str:
    """Converts a Python dictionary to a JSON string.

    Args:
        parsable_dictionary: dict
            The dictionary to convert.
        **kwargs:
            Additional keyword arguments to pass to json.dumps.

    Returns:
        str:
            The string representation of the dictionary.
    """
    return json.dumps(parsable_dictionary, **kwargs)
