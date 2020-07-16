#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'eugene'

from collections import OrderedDict
import os

'''

    This file is part of 'KoJen'.

    'KoJen' is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'KoJen' is distributed in the hope that it will be useful
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with 'KoJen'.  If not, see <http://www.gnu.org/licenses/>.
    For any requests please contact : koh.jaen@yahoo.de.

'''

''' This forms the base for some sorts of code generation.

    Step 1) Load template files to memory
    Step 2) Search and replace passed-in tags in memory (including filenames).
    
'''

# Code Model -> Just a bunch of lines, mapped to filenames.
class CCodeModel:
    def __init__(self):
        self.filenames_to_lines = OrderedDict()


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

    def __init__(self, inputfiledir, outputfiledir, language=None, author='Anonymous', namespace_to_folders = False):
        self.input_template_file_dir = inputfiledir
        self.output_gen_file_dir = outputfiledir
        self.language = language
        self.author = author
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
                if file.lower().find(filter_files_containing_in_name.lower()) > -1 or not filter_files_containing_in_name.strip():
                    template_file_found = True
                    with open(os.path.join(root, file)) as f:
                        lines = []
                        # Replace the key:value pairs per line...
                        for line in f:
                            for tag, desired_text in dict_to_replace_lines.items():
                                desired_text = self.__preserve_leading_tagwhitespace_in_multiline_searchandreplace(line, tag, desired_text)
                                line = line.replace(tag,desired_text)
                            # split multi-line-in-one-string to multi line. Code preservation does not work otherwise.
                            if line.count('\n') > 1:
                                lines_in_line = line.rstrip('\n').split('\n')
                                for l in lines_in_line:
                                    lines.append(l + '\n')  # could do
                            else:
                                lines.append(line)
                        # Replace the key:value pairs per filename...
                        for tag, desired_text in dict_to_replace_filenames.items():
                            file = file.replace(tag,desired_text)

                        result.filenames_to_lines[file] = lines

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
                    writer.write(line)
