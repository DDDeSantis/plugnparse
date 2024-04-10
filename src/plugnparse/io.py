import os
import tempfile
from pathlib import Path
from datetime import datetime
from distutils.dir_util import copy_tree
import json
import numpy as np


##########################################################################
# File and Directory IO
##########################################################################
def file_exists(filepath):
    if isinstance(filepath, Path):
        if filepath.exists():
            return True
    elif isinstance(filepath, str):
        if os.path.exists(filepath):
            return True
    return False


def is_dir(filepath):
    if isinstance(filepath, Path):
        if filepath.exists() and filepath.is_dir():
            return True
    elif isinstance(filepath, str):
        if os.path.exists(filepath) and os.path.isdir(filepath):
            return True
    return False


def to_path(file_path):
    if isinstance(file_path, Path):
        return file_path
    else:
        return Path(file_path)


def path_to_dir(filepath):
    if file_exists(filepath):
        if is_dir(filepath):
            return filepath
    folders_ = list(filepath.split("/"))
    if "" in folders_:
        folders_.remove("")
    if len(folders_) == 0:
        raise RuntimeError("No folder in path: " + filepath)
    if "." in folders_[-1]:
        if len(folders_) == 1:
            return "./"
        else:
            return folders_[-2]
    else:
        return folders_[-1]


def create_directories(filepath):
    if isinstance(filepath, Path):
        if not filepath.exists() and filepath.suffix == "":
            os.makedirs(filepath)
    elif isinstance(filepath, str):
        if not os.path.exists(filepath):
            os.makedirs(filepath)


def get_temp_dir():
    return tempfile.gettempdir()


def all_subdirs_of(b='.'):
    result = []
    for d in os.listdir(b):
        bd = os.path.join(b, d)
        if os.path.isdir(bd): result.append(bd)
    return result


def get_latest_folder(top_folder):
    all_subdirs = all_subdirs_of(b=top_folder)
    latest_subdir = max(all_subdirs, key=os.path.getctime)
    return latest_subdir


def get_all_folders_with_subfolder(top_level, subfolder_name):
    subdirectories = all_subdirs_of(top_level)
    result = []
    for d in subdirectories:
        subsubfolders = all_subdirs_of(d)
        for sd in subsubfolders:
            dir_ = path_to_dir(d)
            if dir_ == subfolder_name:
                result.append(sd)
    return result


def copy_folder_contents_to(original_folder, destination_folder):
    create_directories(destination_folder)
    copy_tree(original_folder, destination_folder)


##########################################################################
# Datatime
##########################################################################
def get_date_time_string():
    _now = datetime.now()
    return _now.strftime("%Y_%m_%d-%H_%M_%S")


##########################################################################
# Read and Writing
##########################################################################
def read_json_file(file, **kwargs):
    with open(file, "r") as f:
        return json.load(f, **kwargs)


def write_to_json_file(file, json_obj, **kwargs):
    with open(file, "w") as f:
        json.dump(json_obj, f, **kwargs)


##########################################################################
# Serialization
##########################################################################
def from_json_str(input_str, **kwargs):
    return json.loads(input_str, **kwargs)


def to_json_str(json_obj, **kwargs):
    return json.dumps(json_obj, **kwargs)
