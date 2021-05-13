#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'eugene'

from collections import OrderedDict
import os, shutil
try:
	from .preservative import *
except (ModuleNotFoundError, ImportError) as e:
	from preservative import *

'''

    MIT License

    Copyright (c) 2015 Eugene Grobbelaar (email : koh.jaen@yahoo.de)

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

'''

''' This forms the base for some sorts of code generation.

    Step 1) Load template files to memory
    Step 2) Search and replace passed-in tags in memory (including filenames).
    
'''

# Code Model -> Just a bunch of lines, mapped to filenames.
class CCodeModel:
    def __init__(self):
        self.filenames_to_lines = OrderedDict()

    def Merge(self, codemodel):
        """
        Will merge the input codemodel with this.

        @param codemodel: a CCodeModel object
        """
        self.filenames_to_lines.update(codemodel.filenames_to_lines)


'''------------------------------------------------------------------------------------------------------'''
alpha = 97


def __getnextalphabet__():
    global alpha
    alpha = alpha + 1
    if alpha == 120:
        alpha = 65
    if alpha == 91:
        alpha = 97


def __resetalphabet__():
    global alpha
    alpha = 97


def even_space(str, nospaces=35):
    return str + (nospaces - len(str)) * " "


'''------------------------------------------------------------------------------------------------------'''


class CBASEGenerator:

    def __init__(self, inputfiledir, outputfiledir, language=None, author='Anonymous', group='', brief='',namespace_to_folders = False):
        self.input_template_file_dir = inputfiledir
        self.output_gen_file_dir = outputfiledir
        self.language = language
        self.author = author
        self.group = group
        self.brief = brief
        self.NAMESPACE_TO_GO_TO_OWN_FOLDER = namespace_to_folders
        # Does the input exist
        if not os.path.exists(inputfiledir):
            raise Exception("Directory '" + inputfiledir + "' does not exist.")
        else:
            files = os.listdir(inputfiledir)
            # Is the input empty
            if not files:
                raise Exception("Directory '" + inputfiledir + "' is empty.")
            else:
                # Check the output dir
                if not os.path.exists(outputfiledir):
                    os.makedirs(outputfiledir)
                    print("Directory '" + outputfiledir + "' does not exist...created.")

    def __generate_filenames_from_templates__(self,file, dict_to_replace_filenames):
        for tag, desired_text in dict_to_replace_filenames.items():
            file = file.replace(tag, desired_text)
        return file

    def __loadtemplates_firstfiltering_FILE__(self, filepath, dict_to_replace_lines, dict_to_replace_filenames, filter_files_containing_in_name = ""):
        result = CCodeModel()
        if os.path.exists(filepath):
            file_without_path = os.path.basename(filepath)
            with open(filepath) as f:
                lines = []
                # Replace the key:value pairs per line...
                for line in f:
                    for tag, desired_text in dict_to_replace_lines.items():
                        desired_text = self.__preserve_leading_tagwhitespace_in_multiline_searchandreplace(line, tag, desired_text)
                        line = line.replace(tag, desired_text)
                    # split multi-line-in-one-string to multi line. Code preservation does not work otherwise.
                    if line.count('\n') > 1:
                        lines_in_line = line.rstrip('\n').split('\n')
                        for l in lines_in_line:
                            lines.append(l + '\n')  # could do
                    else:
                        lines.append(line)
                # Replace the key:value pairs per filename...
                for tag, desired_text in dict_to_replace_filenames.items():
                    file_without_path = file_without_path.replace(tag, desired_text)
                result.filenames_to_lines[file_without_path] = lines
        return result

    def __loadtemplates_firstfiltering__(self, dict_to_replace_lines, dict_to_replace_filenames, filter_files_containing_in_name = ""):
        """
        Load Template and do 1st round of filtering. The filtering will replace the TAG

        @param dict_to_replace_lines: a dictionary of keys:values to replace per line
        @param dict_to_replace_filenames:  a dictionary of keys:values to replace per templatefilename. This includes extension.
        @param filter_files_containing_in_name:  fill process only files that contain this text in the name...or "" for all.
        @return: CCodeModel, a dictionary -> {filename,[lines]}
        """
        template_file_found = False
        result = CCodeModel()
        CWD = self.input_template_file_dir
        for root, dirs, files in os.walk(CWD):
            for file in files:
                if (file.lower().find(filter_files_containing_in_name.lower()) > -1 or not filter_files_containing_in_name.strip()) and not file.lower().find(".removed") > -1 :
                    template_file_found = True
                    cm = self.__loadtemplates_firstfiltering_FILE__(os.path.join(root, file), dict_to_replace_lines, dict_to_replace_filenames, filter_files_containing_in_name)
                    result.Merge(cm)

        if not template_file_found:
            raise Exception("Directory '" + self.input_template_file_dir + "' contains no templates.")

        return result

    def __preserve_leading_tagwhitespace_in_multiline_searchandreplace(self, line, tag, desired_text):
        """
        For the case where the 'desired_text' that should replace the 'tag' in the 'line', if it is a multi-line
        replace, it will keep the leading spaces across all lines...otherwise simply returns the input desired_text
        @param line:
        @param tag:
        @param desired_text:
        @return:
        """
        if line.find(tag) != -1:
            desired_text_as_lines = desired_text.rstrip('\n').split('\n')
            if len(desired_text_as_lines) > 1:
                leading_spaces = (len(line) - len(line.lstrip(' '))) * " "
                desired_text = ""
                for d in desired_text_as_lines:
                    if not desired_text:
                        desired_text = d + "\n"
                    else:
                        desired_text = desired_text + leading_spaces + d + "\n"
                desired_text = desired_text.rstrip('\n')

        return desired_text

    def __createoutput__(self, filenames_to_lines):
        for f in filenames_to_lines:
            print("+++++++++ ", f)
            filename = os.path.join(self.output_gen_file_dir, f)

            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, 'w') as writer:
                for line in filenames_to_lines[f]:
                    line = line.replace('\t',"    ") # Last filter! Convert tabs to 4 spaces...
                    writer.write(line)

    '''Will use the base-class configured 'output directory' if no preserve directory is passed in. '''
    def __preserve_usertags_in_files__(self, codemodel, preserve_dir = ""):
        # Round-trip Code Preservation. Will load the code to preserve upon creation (if the output dir is not-empty/the same as the one in the compile path).
        # TCP gen might have a different output directory (typically COG will put files into an intermediate dir, and them copy them elsewhere
        ## Preserve only files...
        for filename_nopath in codemodel.filenames_to_lines:
            file_to_preserve = ""
            if preserve_dir == "":
                file_to_preserve = os.path.join(self.output_gen_file_dir, filename_nopath)
            else:
                file_to_preserve = os.path.join(preserve_dir, filename_nopath)
            preservation = Preservative(file_to_preserve)
            preservation.Emplace(codemodel.filenames_to_lines)

        ## Preserve the entire directory
        # preservation = None
        # if preserve_dir == "":
        #    preservation = Preservative(self.output_gen_file_dir)
        # else:
        #    preservation = Preservative(preserve_dir)
        # preservation.Emplace(codemodel.filenames_to_lines)
'''------------------------------------------------------------------------------------------------------'''


def FileCopyUtil(dir_from, dir_to, list_of_filenames):
    """
    Will copy each file from list_of_filenames in dir_from to dir_to.
    Will create dir_to (even if its a tree) if it does not exist.

    @param dir_from: The directory from, where the list of files reside.
    @param dir_to: The directory the list of files should be copied to.
    @param list_of_filenames: The list [] of filenames to be copied.
    """
    try:
        os.makedirs(dir_to, exist_ok=True)
        for filename in list_of_filenames:
            try:
                shutil.copy(os.path.join(dir_from, filename), os.path.join(dir_to, filename))
            except OSError:
                print("Copy of the file %s failed" % os.path.join(dir_from, filename))
    except OSError:
        print("Creation of the directory %s failed" % dir_to)