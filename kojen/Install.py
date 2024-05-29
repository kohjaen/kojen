#!/usr/bin/env python3
import os
from .cgen import FileCopyUtil
from distutils.dir_util import copy_tree
import shutil

def getUserTemplateRoot() -> str:
    """Returns the user template path as an absolute path"""
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), "user_templates")

def _checkPath(template_path) -> bool:
    # Check if path exists ...
    if not template_path.strip():
        print("Error : path empty. Aborting.")
        return False
    if not os.path.isfile(template_path) and not os.path.isdir(template_path):
        print("Error : path '" + template_path + "' does not exist. Aborting.")
        return False
    return True

def InstallTemplates(template_path) -> None:
    """Will install the provided template path to the 'user templates' folder. If path is a single file, only the single file
       will be copied. It it is a directory, the tree will be preserved."""

    if _checkPath(template_path):
        if os.path.isfile(template_path):
            FileCopyUtil(os.path.dirname(os.path.abspath(template_path)), getUserTemplateRoot(), [os.path.basename(os.path.abspath(template_path))])
        if os.path.isdir(template_path):
            copy_tree(os.path.abspath(template_path), getUserTemplateRoot())

def UninstallTemplates() -> None:
    """Will uninstall all user templates."""

    if _checkPath(getUserTemplateRoot()):
        shutil.rmtree(getUserTemplateRoot())

def ContainsTemplates(rel_template_path) -> bool:
    """Will indicate if a user template, by relative path, has already been installed. This can be a file or a folder."""
    if not os.path.exists(getUserTemplateRoot()):
        return False

    isFile = os.path.isfile(rel_template_path) or rel_template_path.find(".") > -1
    isDir = os.path.isdir(rel_template_path) or rel_template_path.find(".") == -1

    for root, dirs, filenames in os.walk(getUserTemplateRoot()):
        if isFile:
            for filename in filenames:
                normpath_file = os.path.normpath(os.path.join(root, filename))
                if normpath_file.find(os.path.normpath(rel_template_path)) != -1:
                    return True
        if isDir:
            for dirname in dirs:
                normpath_file = os.path.normpath(os.path.join(root, dirname))
                if normpath_file.find(os.path.normpath(rel_template_path)) != -1:
                    return True
    return False


